I installed cairosvg to convert svg files to pdf files. Install with:

    sudo pip install cairosvg

This will convert an svg to pdf:

    cairosvg test.svg -o test.pdf -d 100

Then this will print a pdf:

    lpr -P HP_LaserJet_200_colorMFP_M276nw__4EADB6_ test.pdf
