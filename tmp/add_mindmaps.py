from pathlib import Path
import shutil
p=Path('units/ecology/book/ecology-1A-2C.tex');s=p.read_text();shutil.copy(p,'tmp/pdfs/ecology-before-mindmaps.tex');shutil.copy('output/pdf/ecology-1A-2C.pdf','tmp/pdfs/ecology-before-mindmaps.pdf')
maps=[
('Mind map: how we explain living systems','maplife','1A + 1B', 'How do we explain living systems?',
 [('Evidence and reasoning','begins with','Observations and measurements','support or challenge','Testable explanations','use to predict','New results can revise an explanation'),('Life and metabolism','depends on','Cells and genetic information','organize','Chemical reactions','transfer energy for','Growth, repair, and cellular work'),('Homeostasis','regulates','Internal conditions within ranges','uses responses in','Feedback loops','negative feedback','Opposes the initiating change')],
 r'\textbf{Connection to explain.} A person shivers when cold: temperature change is the stimulus; muscle activity uses ATP; metabolism releases heat; warming reduces the need to shiver. Evidence is needed to test each proposed relationship.',
 r'\textbf{Common mix-up.} An observation records what was detected. An inference interprets it. Metabolism describes reactions; homeostasis describes regulation. Positive feedback amplifies change and needs an endpoint.',
 r'\textbf{Close the book.} Draw three branches from memory. Explain how an experiment could test one response to a change in temperature.',
 r'Read more: reasoning, page \pageref{onea}; life, page \pageref{lifecheck}; feedback, page \pageref{feedback}.'),
('Mind map: energy flows and matter cycles','mapenergy','1C', 'How does an ecosystem function?',
 [('Energy enters','usually as','Sunlight','captured by','Photosynthetic producers','make organic food for','Consumers and decomposers'),('Cells use energy','through','Cellular respiration','transfers fuel energy to','ATP','powers','Movement, synthesis, and transport'),('Matter is reused','through','Feeding, waste, and decomposition','move and rearrange','Atoms and nutrients','can be taken up by','Producers again')],
 r'\textbf{Connect the branches.} Producers use light energy to build organic molecules. Feeding transfers those molecules and their energy. Producers, consumers, and decomposers use cellular metabolism and release heat.',
 r'\textbf{Follow two different paths.} Food energy eventually dissipates as heat; atoms remain in matter and can be reused. Plants perform both photosynthesis and cellular respiration. Chemical energy supports chemosynthetic producers where sunlight is not the source.',
 r'\textbf{Close the book.} Trace one carbon atom and one energy pathway through grass, a rabbit, and decomposers. Explain why the two paths do not have the same ending.',
 r'Read more: energy and matter, page \pageref{onec}; gas arrows, page \pageref{gases}; pyramids, page \pageref{pyramids}.'),
('Mind map: biodiversity, threats, and populations','mapchange','2A + 2B + 2C','What changes an ecosystem?',
 [('Biodiversity','includes','Genetic, species, and ecosystem diversity','can support','Resilience and ecosystem functions','benefit people as','Ecosystem services'),('Human activities','can create','CHIPPO threats','can reduce','Habitat quality and connectivity','can be addressed by','Protection, restoration, and corridors'),('Population change','depends on','Births + immigration versus deaths + emigration','interact with','Resources and limiting factors','help determine','Carrying capacity and growth patterns')],
 r'\textbf{Read across the branches.} A road can remove habitat and isolate populations. Reduced resources can lower carrying capacity; isolation can reduce gene flow. A suitable crossing improves connectivity but does not solve every limiting factor.',
 r'\textbf{Remember the qualifications.} Biodiversity can support resilience; it does not guarantee survival. Carrying capacity can change. An earlier Overshoot Day indicates greater demand relative to regeneration, not a direct species count.',
 r'\textbf{Close the book.} Start with drought or habitat loss. Draw a chain connecting a limiting factor, population change, biodiversity, and one service used by people. Label uncertain outcomes with ``can''.',
 r'Read more: biodiversity, page \pageref{twoa}; CHIPPO, page \pageref{twob}; populations, page \pageref{twoc}; resources, page \pageref{resources}.')]
parts=[]
for title,label,targets,root,branches,connect,trap,recall,refs in maps:
 a=[rf'\pagechapter{{{title}}}{{{label}}}',rf'\idea{{{targets}: begin with the central question, then follow each branch. Read an arrow together with the boxes it connects.}}',r'\begin{center}',r'\begin{tikzpicture}[concept/.append style={text width=3.55cm,minimum height=1.1cm},rel/.append style={text width=3.2cm}]',rf'\node[concept,fill=forest,text=white,text width=5.5cm] (root) at (5.2,0) {{{root}}};']
 for i,b in enumerate(branches):
  x=i*5.2;col=['blue','forest','orange'][i]
  a += [rf'\node[concept,draw={col},fill={col}!10] (b{i}) at ({x},-2.3) {{\textbf{{{b[0]}}}}};',rf'\draw[flow,draw={col}] (root.south)--++(0,-0.55)-|(b{i}.north);']
  for j in range(3):
   y=-4.9-j*2.6;a += [rf'\node[concept,draw={col},fill={col}!5] (n{i}{j}) at ({x},{y}) {{{b[2+j*2]}}};']
   prev=f'b{i}' if j==0 else f'n{i}{j-1}'
   a += [rf'\draw[flow,draw={col}] ({prev})--node[rel]{{{b[1+j*2]}}}(n{i}{j});']
 a += [r'\end{tikzpicture}\par',r'\end{center}',connect,trap,recall,r'{\small '+refs+r'\par}',r'{\footnotesize Original study map synthesizing the class materials cited in the linked sections.\par}']
 parts.append('\n'.join(a))
marker=r'\pagechapter{1A\quad Evidence and scientific reasoning}{onea}'
s=s.replace(marker,'\n\n'.join(parts)+'\n\n'+marker)
s=s.replace(r'\subsection*{Three connections to explain}',r'\textbf{Zoom in.} Use the next three mind maps for living systems (page \pageref{maplife}), energy and matter (page \pageref{mapenergy}), and ecological change (page \pageref{mapchange}). Then return here to connect the topics.\n'.replace(r'\n','\n')+r'\subsection*{Three connections to explain}')
p.write_text(s)
for f in ['README.md','units/ecology/book/README.md','units/ecology/materials-index.md']:
 p=Path(f);s=p.read_text().replace('35-page','38-page').replace('35 pages','38 pages');p.write_text(s)
p=Path('units/ecology/book/README.md');s=p.read_text();s+='\n## Mind maps\n\nThree topic mind maps follow the whole-unit knowledge graph: living systems (1A–1B), energy and matter (1C), and ecological change (2A–2C). Labeled branches, cross-topic examples, common confusions, and redraw prompts support understanding and recall. All maps are editable TikZ.\n';p.write_text(s)
