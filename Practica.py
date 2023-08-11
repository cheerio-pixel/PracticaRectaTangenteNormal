import math
import flask
from flask import Flask, render_template, send_file, jsonify, request
import html
import base64
import sympy
from sympy.parsing.sympy_parser import parse_expr
from sympy.printing.latex import latex  # Latex ftw
from sympy import Symbol, lambdify, oo, zoo, nan, nsimplify, Number
import io
import matplotlib
import matplotlib.pyplot as plt
import numpy as np


# Renderiza latex
## Lee https://matplotlib.org/stable/tutorials/text/mathtext.html
## Matplotlib ya tiene su renderizador de latex
# plt.rcParams['text.usetex'] = True
# Dependencias para arch linux
# - extra/texlive-fontsrecommended

matplotlib.rcParams.update({"font.size": 22})
# Usa un backend no interactivo
matplotlib.use("agg")

OK = 0
PARSING_ERROR = -1
CONSTANT_VALUE_ERROR = -2
INCORRECT_VARIABLE_ERROR = -3
OUTSIDE_DOMAIN_ERROR = -4
DIVISION_BY_ZERO_ERROR = -5


# Excepcion custom para funciones matematicas fuera del rango
class OutsideDomainError(Exception):
    pass


app = Flask(__name__, template_folder="", static_folder="static")


def recta_tangente(f: sympy.Expr, a: float):
    x = Symbol("x")
    df = sympy.diff(f)
    return f.subs(x, a) + df.subs(x, a) * (x - a)


def recta_normal(f: sympy.Expr, a: float):
    x = Symbol("x")
    df = sympy.diff(f)
    return f.subs(x, a) - 1 / df.subs(x, a) * (x - a)


def has_infty(expr):
    return expr.has(oo, -oo, zoo, nan)

def round_expr(expr, num_digits):
    # Trunca numeros de coma flotante
    return expr.xreplace({n: round(n, num_digits) for n in expr.atoms(Number)})


def plot(
    f: sympy.Expr, c: float, has_normal=True, has_tangent=True
) -> io.BytesIO:
    funcion = lambdify("x", f, "math")
    try:
        f_de_c = funcion(c)
    except ValueError as e:  # Outside of range error, maybe
        raise OutsideDomainError(e)

    try:
        x = np.linspace(c - 10, c + 10, 1_000)
    except ValueError as e:
        raise OutsideDomainError(e)
    fig, ax = plt.subplots(figsize=(10, 10), tight_layout=True)
    # Añade una linea vertical y horizontal en el origen
    ax.axhline(0, color="black", linewidth=2)
    ax.axvline(0, color="black", linewidth=2)

    if has_tangent:
        expr_tangente = recta_tangente(f, c)
        tangente = lambdify("x", expr_tangente, "math")
        # No hay cosa que un simple map no resuelva
        ax.plot(
            x,
            list(map(tangente, x)),
            label=f"Recta Tangente ${latex(nsimplify(round_expr(expr_tangente, 6)))}$",
            color="blue",
        )
    if has_normal:
        expr_normal = recta_normal(f, c)
        normal = lambdify("x", expr_normal, "math")
        if has_infty(expr_normal):
            expr_normal = oo
            ax.axvline(
                c, label=f"Recta Normal ${latex(nsimplify(round_expr(expr_normal, 6)))}$", color="red"
            )
        else:
            ax.plot(
                x,
                list(map(normal, x)),
                label=f"Recta Normal ${latex(nsimplify(round_expr(expr_normal, 6)))}$",
                color="red",
            )
    ax.plot(
        x, list(map(funcion, x)), label=f"Funcion ${latex(nsimplify(round_expr(f, 6)))}$", color="green"
    )  # Dibuja de ultimo
    ax.legend(
        bbox_to_anchor=(0.1, 1.5),
        loc="upper left",
        fancybox=True,
        shadow=True,
    )

    plt.ylim([f_de_c - 10, f_de_c + 10])
    plt.grid(visible=True)
    # plt.show() # Entorno interactivo
    # Salva la imagen en memoria
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    # Setea el puntero para que lea desde el inicio
    buf.seek(0)
    return buf


def report_error(error_code: int):
    return jsonify({"result": None, "status": error_code})


@app.route("/")
def main():
    return send_file("prac.html")


# URL /pyplot/&f="PYTHON EXPRESSION"&c=float
@app.route("/pyplot/")
def pyplot():
    try:
        f = parse_expr(html.escape(request.args.get("f")))
    except Exception:
        # Expresion ingresada es invalida, comprueba la sintaxis o si
        # estas usando una variable distinta de x
        return report_error(PARSING_ERROR)
    try:
        c = float(request.args.get("c"))
    except Exception:
        # El numero ingresado no es valido
        return report_error(CONSTANT_VALUE_ERROR)
    # Genera todas las compbinaciones posible
    try:
        plot_buffers = [plot(f, c, x, y) for x in range(2) for y in range(2)]
    except ValueError:
        return report_error(INCORRECT_VARIABLE_ERROR)
    except TypeError:
        return report_error(INCORRECT_VARIABLE_ERROR)
    except OutsideDomainError:
        return report_error(OUTSIDE_DOMAIN_ERROR)
    except ZeroDivisionError:
        return report_error(DIVISION_BY_ZERO_ERROR)
    # ya que un buffer de bytes no es json-serializables tenemos que encodearlo
    # Despues tambien en caracteres ascii ya que los bytes tampoco son serializables
    encoded_imges = [
        base64.encodebytes(buffer.getvalue()).decode("ascii")
        for buffer in plot_buffers
    ]
    return jsonify({"result": encoded_imges, "status": 0})


# x = Symbol('x')
# plot(-x**3 + 6*x**2, 1)
