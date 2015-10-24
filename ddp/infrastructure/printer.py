import subprocess
import cairosvg


def graph_to_svg(graph):
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="850" version="1.1">\n'
    for ((x1, y1), (x2, y2)) in graph.edges_iter():
        line = '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" stroke="black" stroke-width="2" />\n'.format(
            x1, y1, x2, y2)
        svg += line
    svg += '</svg>'
    return svg


def write_file(file_name, contents):
    text_file = open(file_name, "w")
    text_file.write(contents)
    text_file.close()


def svg_to_pdf(svg_file_name, pdf_file_name):
    # http://cairosvg.org/user_documentation/#idapi
    return cairosvg.svg2pdf(url=svg_file_name)


def print_pdf(pdf_file_name):
    # does not work for me: HP_LaserJet_200_colorMFP_M276nw__4EADB6_
    subprocess.call([
        "lpr",
        "-P", "HP-LaserJet-200-colorMFP-M276nw",
        pdf_file_name
    ])
