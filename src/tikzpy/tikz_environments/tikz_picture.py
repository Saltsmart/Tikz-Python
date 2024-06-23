import subprocess
import webbrowser
from shutil import rmtree, copy
import re
import numpy as np
from pathlib import Path
from typing import List, Optional
from tikzpy.tikz_environments.scope import Scope
from tikzpy.tikz_environments.tikz_environment import TikzEnvironment
from tikzpy.tikz_environments.tikz_style import TikzStyle
from tikzpy.utils.helpers import (
    brackets,
    true_posix_path,
    replace_code,
    find_image_start_boundary,
    find_image_end_boundary,
)
from tikzpy.templates.tex_file import TEX_FILE
from pdf2image import convert_from_path
from PIL import Image

try:
    from IPython import get_ipython
    from IPython.display import display

    ipython = get_ipython()
    if ipython is None:
        JUPYTER_ENABLED = False
    if "IPKernelApp" in ipython.config:  # Jupyter notebook or qtconsole
        JUPYTER_ENABLED = True
except ImportError:
    JUPYTER_ENABLED = False


class TikzPicture(TikzEnvironment):
    """
    A class for managing a Tikzpicture environment and associated tex files with tikz code.

    The TikzPicture class acts a canvas in which users can append drawings to.
    In the background, the TikzPicture manages the creation of
    the tikz code.

    Parameters:
        center: True/False if one wants to center their Tikz code
        options: A list of options for the Tikz picture
    """

    def __init__(
        self, center: bool = False, options: str = "", tikz_code_dir=None
    ) -> None:
        super().__init__(options)
        self._preamble = {}
        self._postamble = {}
        self.BASE_DIR = None
        self.TEMP_DIR = Path.cwd() / f".tikz_tmp{id(self)}"

        if tikz_code_dir is not None:
            self.BASE_DIR = Path(tikz_code_dir)

        if center:
            self._preamble["center"] = "\\begin{center}\n"
            self._postamble["center"] = "\\end{center}\n"
        else:
            self._preamble["center"] = ""
            self._postamble["center"] = ""

    def code(self) -> str:
        """Returns a string contaning the generated Tikz code."""
        code = ""
        # Add the beginning statement
        for stmt in self._preamble.values():
            code += stmt
        code += f"\\begin{{tikzpicture}}{brackets(self.options)}\n"

        # Add the main tikz code
        for draw_obj in self.drawing_objects:
            code += "    " + draw_obj.code + "\n"

        # Add the ending statement
        code += "\\end{tikzpicture}\n"
        for stmt in list(reversed(list(self._postamble.values()))):
            code += stmt
        return code

    def __repr__(self) -> str:
        readable_code = f"\\begin{{tikzpicture}}{brackets(self.options)}\n"

        for draw_obj in self.drawing_objects:
            readable_code += "    " + draw_obj.code + "\n"

        readable_code += "\\end{tikzpicture}\n"
        return readable_code

    def tikzset(self, style_name: str, style_rules: TikzStyle) -> TikzStyle:
        """Create and add a TikzStyle object with name "style_name" and tikzset syntax "style_rules" """
        style = TikzStyle(style_name, style_rules)
        self.add_styles(style)
        return style

    def add_styles(self, *styles: List[TikzStyle]) -> None:
        """Add a TikzStyle object to the environment."""
        for style in styles:
            self._preamble[f"tikz_style:{style.style_name}"] = style.code

    def set_tdplotsetmaincoords(self, theta: float, phi: float) -> None:
        """Specify the viewing angle for 3D.

        theta: The angle (in degrees) through which the coordinate frame is rotated about the x axis.
        phi: The angle (in degrees) through which the coordinate frame is rotated about the z axis.
        """
        self.tdplotsetmaincoords = (theta, phi)
        self._preamble[
            "tdplotsetmaincoords"
        ] = f"\\tdplotsetmaincoords{{{theta}}}{{{phi}}}\n"

    def write_tex_file(self, tex_filepath):
        tex_code = TEX_FILE
        tex_file_contents = re.sub("fillme", lambda x: self.code(), tex_code)
        # Update the TeX file
        if self.BASE_DIR is not None:
            tex_filepath = self.BASE_DIR / tex_filepath

        with open(tex_filepath, "w") as f:
            f.write(tex_file_contents)

    def write(self, tikz_code_filepath=None):
        if tikz_code_filepath is None:
            tikz_code_filepath = "tikz_code.tex"

        base_dir: Path = Path.cwd()
        if self.BASE_DIR is not None:
            base_dir = self.BASE_DIR

        tikz_code_filepath = base_dir / tikz_code_filepath
        with open(tikz_code_filepath, "w") as f:
            f.write(self.code())

    def compile(
        self, pdf_destination: Optional[str] = None, quiet: bool = True
    ) -> Path:
        """Compiles the Tikz code and returns a Path to the final PDF.
        If no file path is provided, a default value of "{self.TEMP_DIR}/temp.pdf" will be used.

        Parameters:
            pdf_destination (str): The file path of the compiled pdf.
            quiet (bool): Parameter to silence latexmk.
        """
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        tex_filepath = self.TEMP_DIR / "temp.tex"
        self.write_tex_file(tex_filepath)

        tex_file_posix_path = true_posix_path(tex_filepath)
        tex_file_parents = true_posix_path(tex_filepath.parent)
        options = ""
        if quiet:
            options += " -quiet "
        subprocess.run(
            f"latexmk -pdf {options} -output-directory={tex_file_parents} -aux-directory={tex_file_parents} {tex_file_posix_path}",
            shell=True,
        )

        pdf_file = tex_filepath.with_suffix(".pdf")
        if pdf_destination is not None:
            copy(pdf_file, pdf_destination)
            pdf_file = Path(pdf_destination)
        return pdf_file.resolve()

    def save_png(self, pdf_fp, png_destination):
        page_pngs = convert_from_path(pdf_fp)

        # Create the png of the pdf
        total = len(page_pngs)
        ind = 0
        if total > 1:
            print(
                f"WARNING! {pdf_fp=} has more than two pages, expected only one. Going to use"
                " the last page. "
            )
            ind = len(page_pngs) - 1
        page_pngs = list(page_pngs)
        image = page_pngs[ind]
        print(f"Converting page {ind}/{total}")
        # easier to find boundaries of a grayscale image
        grayscale_image = image.convert("L")
        img_data = np.asarray(grayscale_image)
        y_0 = find_image_start_boundary(img_data)
        y_1 = find_image_end_boundary(img_data)
        x_0 = find_image_start_boundary(img_data.T)
        x_1 = find_image_end_boundary(img_data.T)
        horizontal_len = len(img_data.T)
        vertical_len = len(img_data.T)
        # Zoom in the picture
        x_0 = int(min(0.20 * horizontal_len, x_0))
        x_1 = int(max(0.80 * horizontal_len, x_1))
        # Add vertical whitespace padding
        y_0 = int(max(0, y_0 - 0.02 * vertical_len))
        y_1 = int(min(vertical_len, y_1 + 0.02 * vertical_len))

        true_img = image.convert("RGB")
        img_data = np.asarray(true_img)
        cropped_img_data = img_data[y_0:y_1, x_0:x_1]
        cropped_img = Image.fromarray(np.uint8(cropped_img_data))
        cropped_img.save(str(png_destination), "PNG")

    def show(self, quiet: bool = False) -> None:
        """Compiles the Tikz code and displays the pdf to the user. Set quiet=True to shut up latexmk.
        This should either open the PDF viewer on the user's computer with the graphic,
        or open the PDF in the user's browser.
        """
        pdf_file = self.compile(quiet=quiet)
        if JUPYTER_ENABLED:
            page_pngs = convert_from_path(pdf_file, transparent=True)
            for img in page_pngs:
                display(img)
        else:
            webbrowser.open_new(str(pdf_file.as_uri()))

    def close(self) -> None:
        if self.TEMP_DIR is not None and self.TEMP_DIR.is_dir():
            rmtree(self.TEMP_DIR)

    def scope(self, options: str = "") -> Scope:
        scope = Scope(options=options)
        self.draw(scope)
        return scope
