"""What is an area? One film, one set of lines, shape after shape.

    .venv/bin/python mathematics/area/main.py

Lines stack into a rectangle, slide into a parallelogram, and split into a
triangle. Their lengths then explain a trapezoid and circle. Finally, thinner
strips show how an integral measures the area under a curve.
"""

from film import AreaFilm


def main() -> None:
    output = AreaFilm().render()
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
