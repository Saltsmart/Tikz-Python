# Tikz-Python
An object-oriented Python approach towards providing a giant wrapper for Tikz code, with the goal of streamlining the process of creating complex figures for TeX documents.

## Documentation

We have documentation now! Please visit the [documentation](todo) site.

## Requirements
This requires Python 3.7+ Additionally, you need an up-to-date version of a LaTeX that has both the `tikz` library and `latexmk`. 

If you already have LaTeX or a related TeX engine, you most definitely have `tikz`. You also probably have `latexmk`. If you're not sure, run `latexmk --version` from the command line and observe the output.

## Installation 
You can install Tikzpy as follows.
```bash
$ git clone https://github.com/ltrujello/Tikz-Python
$ cd Tikz-Python
$ pip install -e .
```
If you additionally want to check that everything is working normally, run 
```bash
$ pip install -r requirements.txt
$ make test 
```
All test cases should pass. Let me know if that is not the case.

## How to Use: Basics
An example of this package in action is below. 
```python
from tikzpy import TikzPicture  # Import the class TikzPicture

tikz = TikzPicture()
tikz.circle((0, 0), 3, options="thin, fill=orange!15")

arc_one = tikz.arc((3, 0), 0, 180, x_radius=3, y_radius=1.5, options="dashed")
arc_two = tikz.arc((-3, 0), 180, 360, x_radius=3, y_radius=1.5)

tikz.write()  # Writes the Tikz code into a file
tikz.show()  # Displays a pdf of the drawing to the user
```
which produces
<img src="https://github.com/ltrujello/Tikz-Python/blob/main/examples/basic/basic.png"/> 

We explain line-by-line the above code.

* `from tikzpy import TikzPicture` imports the `TikzPicture` class from the `tikzpy` package. 

* The second line of code is analogous to the TeX code `\begin{tikzpicture}` and `\end{tikzpicture}`. The variable `tikz` is now a tikz environment, specifically an instance of the class `TikzPicture`, and we can now append drawings to it.

* The third, fourth, and fifth lines draw a filled circle and two elliptic arcs, which give the illusion of a sphere.

* In the last two lines, `write()` writes all of our tikz code into a file located at `tikz_code/tikz_code.tex`. The call `show()` immediately displays the PDF of the drawing to the user.

