from pathlib import Path
import shutil
p=Path('units/ecology/book/ecology-1A-2C.tex');s=p.read_text();shutil.copy(p,'tmp/pdfs/ecology-before-open-images.tex');shutil.copy('output/pdf/ecology-1A-2C.pdf','tmp/pdfs/ecology-before-open-images.pdf')
s=s.replace(r'\usepackage{tikz}',r'\usepackage{graphicx}'+'\n'+r'\graphicspath{{units/ecology/book/assets/}{assets/}}'+'\n'+r'\usepackage{tikz}')
start=s.index(r'\begin{center}',s.index(r'\pagechapter{1B\quad Cells and viruses}'))
end=s.index(r'\par'+'\n'+r'\begin{tabularx}',start)
s=s[:start]+r'''\begin{center}
\begin{minipage}[c]{0.68\linewidth}
\centering\textbf{A bacterial cell}\par
\includegraphics[width=\linewidth]{bacterial-cell.png}
\end{minipage}\hfill
\begin{minipage}[c]{0.28\linewidth}
\centering\textbf{Adenovirus}\par
\includegraphics[width=\linewidth]{adenovirus.png}
\end{minipage}
\end{center}
{\small\textbf{Read the illustrations.} The bacterium has cytoplasm, ribosomes, and DNA in a nucleoid region, with no membrane-bound nucleus. The virus model shows the outer protein capsid and projecting fibers; its genome is inside and is not visible. These are illustrative models, not microscope photographs or a size comparison. Not all bacteria have every structure shown, and viruses have different shapes.\par}
{\footnotesize Cell: Mariana Ruiz Villarreal (LadyofHats), \href{https://commons.wikimedia.org/wiki/File:Average_prokaryote_cell-_en.svg}{Wikimedia Commons}, public domain. Virus: Thomas Splettstoesser, \href{https://commons.wikimedia.org/wiki/File:Adenovirus_3D_schematic.png}{Wikimedia Commons}, \href{https://creativecommons.org/licenses/by-sa/4.0/}{CC BY-SA 4.0}. Images reproduced without content changes; scaled for layout.\par}
'''+s[end:]
start=s.index(r'\begin{center}',s.index(r'\pagechapter{2B\quad Habitat loss and corridors}'))
end=s.index(r'\subsection*{Four mechanisms}',start)
s=s[:start]+r'''\begin{center}
\includegraphics[width=0.76\linewidth]{banff-crossing.jpg}
\end{center}
{\small\textbf{A real wildlife crossing.} In this photograph from Banff National Park, Canada, traffic passes beneath a habitat connection across the highway. Compare the route across the top with the road below: the crossing supports connectivity while the road still occupies habitat. The photograph alone cannot show how often animals use it or prove population recovery.\par}
{\footnotesize Photograph: m01229, \href{https://commons.wikimedia.org/wiki/File:Animal_crossing_overpass_in_Banff_National_Park_-_Canada_(26271251055).jpg}{Animal crossing overpass in Banff National Park -- Canada}, Wikimedia Commons, \href{https://creativecommons.org/licenses/by-sa/2.0/}{CC BY-SA 2.0}. Reproduced without content changes; scaled for layout.\par}
'''+s[end:]
p.write_text(s)
p=Path('units/ecology/book/README.md');s=p.read_text().replace('All knowledge graphs are editable TikZ drawings inside the LaTeX source. No external image assets are required.', 'Knowledge graphs remain editable TikZ drawings. The cell and virus illustrations and the Banff crossing photograph are openly licensed Wikimedia Commons assets stored in `assets/`; keep this directory with the LaTeX source. See [image credits](assets/CREDITS.md). Prefer suitable openly licensed images for future biological illustrations; use generation only when needed.');p.write_text(s)
Path('units/ecology/book/assets/CREDITS.md').write_text('''# Image credits

Images downloaded from Wikimedia Commons for the study book. Content is unchanged; display size is adjusted in LaTeX. Each image retains its own license. No generated images are included in this revision.

| Local file | Work and creator | License |
| --- | --- | --- |
| bacterial-cell.png | [Average prokaryote cell–en](https://commons.wikimedia.org/wiki/File:Average_prokaryote_cell-_en.svg), Mariana Ruiz Villarreal (LadyofHats); Wikimedia 1280px PNG rendering | Public domain |
| adenovirus.png | [Adenovirus 3D schematic](https://commons.wikimedia.org/wiki/File:Adenovirus_3D_schematic.png), Thomas Splettstoesser ([scistyle.com](https://www.scistyle.com)) | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| banff-crossing.jpg | [Animal crossing overpass in Banff National Park – Canada](https://commons.wikimedia.org/wiki/File:Animal_crossing_overpass_in_Banff_National_Park_-_Canada_(26271251055).jpg), m01229 | [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/) |

The bacterial cell and virus are illustrative models, not micrographs. Their displayed sizes do not show their relative biological sizes. The Banff image is a photograph of an actual crossing. Reuse the licensed images with these credits and the applicable license links.
''')
