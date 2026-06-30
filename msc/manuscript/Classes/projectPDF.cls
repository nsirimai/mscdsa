% Format for ITB project reports, based on CUEDthesisPSnPDF.cls
% By Geraldine Gray 

%-------------------------- identification ---------------------
\ProvidesClass{Classes/ProjectPDF}
%-------------------------- initial code -----------------------

\LoadClass[a4paper]{book}%


\usepackage{setspace}
\usepackage[nottoc]{tocbibind}
\usepackage{amssymb}
%\usepackage{graphicx}
\usepackage{fancyhdr}
\usepackage{eucal}
\usepackage[english]{babel}
\usepackage[dvipsnames]{color}
\usepackage[perpage]{footmisc}
\usepackage[square, sort, numbers, authoryear]{natbib}
\usepackage{ifthen}
\usepackage{ifpdf}
\usepackage{lmodern}


% Nomenclature
\usepackage{nomencl}
\makenomenclature
\renewcommand\nomgroup[1]{%
  \ifthenelse{\equal{#1}{A}}{%
   \item[\textbf{Roman Symbols}] }{%             A - Roman
    \ifthenelse{\equal{#1}{G}}{%
     \item[\textbf{Greek Symbols}]}{%             G - Greek
      \ifthenelse{\equal{#1}{R}}{%
        \item[\textbf{Superscripts}]}{%              R - Superscripts
          \ifthenelse{\equal{#1}{S}}{%
           \item[\textbf{Subscripts}]}{{%             S - Subscripts
	    \ifthenelse{\equal{#1}{X}}{%
	     \item[\textbf{Other Symbols}]}{{%    X - Other Symbols
	    \ifthenelse{\equal{#1}{Z}}{%
	     \item[\textbf{Acronyms}]}%              Z - Acronyms
              			{{}}}}}}}}}}


    \usepackage[ pdftex, plainpages = false, pdfpagelabels, 
                 pdfpagelayout = OneColumn, % display single page, advancing flips the page - Sasa Tomic
                 bookmarks,
                 bookmarksopen = true,
                 bookmarksnumbered = true,
                 breaklinks = true,
                 linktocpage,
                 pagebackref,
                 colorlinks = false,
                 linkcolor = black,
                 urlcolor  = black,
                citecolor = black,
                anchorcolor = black,
                 hyperindex = true,
                 hyperfigures
                 ]{hyperref} 
    \usepackage[pdftex]{graphicx}
    \DeclareGraphicsExtensions{.png, .jpg, .pdf}

    \pdfcompresslevel=9
    \graphicspath{{Figures/PNG/}{Figures/PDF/}{Figures/}}
    


%A4 settings

   \pdfpageheight=297mm
   \pdfpagewidth=210mm


\setlength{\hoffset}{0.00cm}
\setlength{\voffset}{0.00cm}

\setlength{\evensidemargin}{0.5cm}   %0.5 added to text width below
\setlength{\topmargin}{1mm}
\setlength{\headheight}{14pt}
\setlength{\headsep}{1.00cm}
\setlength{\textheight}{20.84cm}
\setlength{\textwidth}{15cm}   
\setlength{\marginparsep}{1mm}
\setlength{\marginparwidth}{3cm}
\setlength{\footskip}{2.36cm}

\pagestyle{fancy}
\renewcommand{\chaptermark}[1]{\markboth{\MakeUppercase{\thechapter. #1 }}{}}
\renewcommand{\sectionmark}[1]{}
\fancyhf{}
\fancyhead[RO]{\bfseries\rightmark}
\fancyhead[LE]{\bfseries\leftmark}
\fancyfoot[C]{\thepage}
%\renewcommand{\headrulewidth}{0.5pt}
\renewcommand{\headrulewidth}{0pt}  %remove line on top of page. Line above puts that line back in.
\renewcommand{\footrulewidth}{0pt}
\fancypagestyle{plain}{
  \fancyhead{}
  \renewcommand{\headrulewidth}{0pt}
}


%
%
% DECLARATIONS
%
% These macros are used to declare arguments needed for the
% construction of the title page and other preamble.

\def\submissiondate#1{\gdef\@submissiondate{#1}}
\def\degree#1{\gdef\@degree{#1}}
\def\supervisor#1{\gdef\@supervisor{#1}}   	
\def\crest#1{\gdef\@crest{#1}}
\def\module#1{\gdef\@module{#1}}
\def\author#1{\gdef\@author{#1}}


% These macros define an environment for front matter that is always 
% single column even in a double-column document.

\newenvironment{alwayssingle}{%
       \@restonecolfalse\if@twocolumn\@restonecoltrue\onecolumn
       \else\newpage\fi}
       {\if@restonecol\twocolumn\else\newpage\fi}

%define title page layout
\renewcommand{\maketitle}{%
\pagenumbering{roman} % Sasa Tomic
\setcounter{page}{0}  % Sasa Tomic
\begin{alwayssingle}
    \renewcommand{\footnotesize}{\small}
    \renewcommand{\footnoterule}{\relax}
    \thispagestyle{empty}
%  \null\vfill
  \begin{center}
  
  {\large \vspace*{1ex}
  {{\@crest} \par}    
  \vspace*{15mm}}
  
     {\large \vspace*{1ex}
  {{\@degree} \par}   
  
  \vspace*{30mm}
  {{\@module} \par}   
  \vspace*{5mm}  }     
  
 { \LARGE {\bfseries {\@title}} \par}
%       { \Large {\bfseries {\@subtitle}} \par}
{\large \vspace*{15mm} 


{{\LARGE \@author} \par}
    
  
\vspace*{1ex}
{{\LARGE \@supervisor} \par}    
\vspace*{15mm}


  \vspace*{15mm}  
  
  
    {\@submissiondate}}   %end large
  \end{center}
  \null\vfill
\end{alwayssingle}}

% Declaration
%
% The dedication environment makes sure the dedication gets its
% own page and is set out in verse format.

\newenvironment{declaration}
{\begin{alwayssingle}
  \pagestyle{empty}
  \begin{flushleft}
  \vspace*{1.5cm}
  {\LARGE }
  \end{flushleft}
  \vspace{0.5cm}
  \begin{quote} \begin{flushleft}}
{\end{flushleft} \end{quote} \end{alwayssingle}}



%ABSTRACT
%
%The abstract environment puts a large, bold, centered "Abstract" label at
%the top of the page. The abstract itself appears in a quote environment,
%i.e. tabbed in at both sides, and on its own page.

\newenvironment{abstracts} {\begin{alwayssingle} \pagestyle{empty}
  \begin{center}
  \vspace*{1.5cm}
  {\Large \bfseries  Abstract}
  \end{center}
  \vspace{0.5cm}
   \begin{quote}}
{\end{quote}\end{alwayssingle}}


%ROMANPAGES
%
% The romanpages environment set the page numbering to lowercase roman one
% for the contents and figures lists. It also resets
% page-numbering for the remainder of the dissertation (arabic, starting at 1).

\newenvironment{romanpages}
{\setcounter{page}{1}
  \renewcommand{\thepage}{\roman{page}}}
{\newpage\renewcommand{\thepage}{\arabic{page}}}
%{\newpage\renewcommand{\thepage}{\arabic{page}}\setcounter{page}{1}}


%\renewcommand{\cftfigfont}{Figure }
%\renewcommand{\cfttabfont}{Table }


