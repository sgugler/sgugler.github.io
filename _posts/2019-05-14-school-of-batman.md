---
mathjax: true
comments: false
title:  "Notes to the School of Batman Podcast"
date:   2019-05-14 
categories: chemistry 
---

# Notes on the School of Batman Podcast

I was featured on the (all around awesome) podcast [School of Badman](https://figshare.com/collections/School_of_Batman/3982956) to talk about chemistry in general, the field of my research group, theoretical and quantum chemistry, and my own specialization, machine learning in theoretical chemistry. I made this little post here to give some clarifications on things I explained shakily or might need a visualization. I will go through it chronologically. You can find the podcast [here](https://figshare.com/articles/The_Case_Of_Mother_s_Child_Army_-_Stefan_Gugler/8117984) or directly here:
<iframe src="https://widgets.figshare.com/articles/8117984/embed?show_title=1" width="568" height="300" allowfullscreen="true" frameborder="0"></iframe>

## In a Nutshell
When I think of 'lab chemistry', I usually have a synthetical chemist in mind who produces molecules that can be used for a wide variety of tasks like glue, pesticides, plastics or drugs. In the podcast, I use drugs to illustrate my points. An organic chemist might have a procedure like the following:
![Part of the Holton Taxol synthesis](/images/school-of-batman/paclitaxel.png)
This is part of the [first route ever described](https://en.wikipedia.org/wiki/Holton_Taxol_total_synthesis) to synthesize [Taxol](https://en.wikipedia.org/wiki/Paclitaxel) aka Paclitaxel, a drug for chemotherapy. The chemists actually stand at their benches and put chemical 1 in a flask and add _t_-BuLi and hexane, two reagents, and cook ('reflux') it for 5 h and so on and so on. You see this takes a lot of time to prepare, especially if you are the first person ever to try it out and a lot of dead ends are to be expected. Despite me just glossing over it, this is an enormously difficult and tedious process, where a lot of practical knowledge is required.  

In theoretical chemistry (which is sometimes used synonymously with quantum chemistry) what we work with looks more like this:

$$i \hbar \frac{d}{d t}\vert\Psi(t)\rangle = \hat H\vert\Psi(t)\rangle$$

which is called the [Schrödinger Equation](https://en.wikipedia.org/wiki/Schr%C3%B6dinger_equation). It is extremely time consuming to find a solution for this equation for larger molecules like Taxol above. There is an even more accurate equation that also takes into account Einstein's theories (it's called the [Dirac equation](https://en.wikipedia.org/wiki/Dirac_equation)] but you guessed it: it takes even more time to solve it. And bu the way: When I say 'solve it', I mean in all but the most simple cases 'find an approximate solution'. There are many ways to find shortcuts, e.g. by restricting my equations just to one class of molecules (like drug-like molecules.) The shortcut I focus on is machine learning, which is, broadly speaking, a set of statistical methods. Another shortcut is molecular dynamics ('simulate molecules'), which I will explain a bit more below. 

## Drug Development
In drug discovery, in the very first phase of finding a new drug, thousands of molecules will be tested with [high-throughput screening](https://en.wikipedia.org/wiki/High-throughput_screening). Machines and humans try produce systematically new molecules and test them for desired properties. After up to 5 years the first molecules will be tested in living organisms and only then in humans ('clinical trials'.) As you can imagine, this costs a [boatload of money](https://www.genengnews.com/news/vectura-scraps-asthma-drug-device-vr475-after-phase-iii-failure/). One way to cut these costs might be machine learning and [virtual screening](https://en.wikipedia.org/wiki/Virtual_screening) where a vast number of molecules don't even have to be synthesized because we can theoretically predict already on the computer that they might be toxic or that they don't show a desired property. That's where I said 'basically list (the properties) on a piece of paper but on the computer' (strong metaphor game, Stefan, well done.) If we go into very high-dimensional spaces and color all molecules with property A to L, we might get a picture like [this](https://interactive.sketchmap.org/Lysine-Dipeptide), where a molecule is clustered according to some internal angles:

![This is a cluster of the lysine dipeptide conformers.](/images/school-of-batman/chem-space.png)

It's immediately clear that millions of compounds can't really be handled well on your average laptop. To play around with molecule clusters, you should try out [sketchmap](https://interactive.sketchmap.org/Lysine-Dipeptide).

# Machine Learning and a Bit of History
I used the word 'neural winter' in the podcast yet in the literature you would rather read about the 'AI winter'. I was introduced to the concept with the first term, but it means the same: A period starting from the 70ies and peaking in early 90ies where funding for AI was sparse and people were rather pessimistic about progress in AI. Commonly it is even subdivided into the first (1974–1980) and second (1987–1993) AI winter. 
<iframe width="800" height="500" frameborder="0" scrolling="no" src="//plot.ly/~akira70000/4.embed"></iframe>
As you can see in the Figure, it was preceded by the 'golden years'. At latest in 2012, machine learning and AI is back on track with successful application of neural nets and deep learning for a host of problems. Currently, AI and machine learning are revolutionizing large parts of the industry, similarly as when the introduction of the computer turned over many businesses. A [full history on AI](https://en.wikipedia.org/wiki/History_of_artificial_intelligence) is found on Wikipedia and gives a devent overview.

## Pople and Early Computational Chemistry
John Pople was one of the fathers of computational chemistry proper with the developement of the quantum chemical software [Gaussian](https://gaussian.com/). (On a tangent: The course of Gaussian became pretty weird after people got ['banned' from using it](https://www.nature.com/articles/429231a), even [Pople himself](https://web.archive.org/web/20170609073016/http://bannedbygaussian.org/).) He won the [Nobel Prize in 1998](https://www.nobelprize.org/prizes/chemistry/1998/pople/facts/) and he died in 2004, aged 78.

![Pople in all his glory](/images/school-of-batman/pople.jpg)

The computational chemistry we are talking here, is all quantum. Unlike molecular dynamics (mentioned above), which applies Newtonian forces to all the atoms, in quantum chemistry we assume all the atoms behave in a 'quantum way'. Without going into the quantum details here, for us it mainly means that the electrons behave in a very complicated way which in turn results in long computing time. The Newtonian picture (molecular dynamics) ignores electrons and is therefore much faster for molecules of the same size, yet much less accurate, because the world is fundamentally quantum (we think.) When we want to check out really large molecules like proteins, we adapt the Newtonian picture, because a quantum calculation could take millions of years. Here is a very small protein as illustration. It's [gramicidin S](https://en.wikipedia.org/wiki/Gramicidin_S), an antibiotic.

![Pople in all his glory](/images/school-of-batman/gramicidin.png)

It has 174 atoms. When we compare that to the tiny H2O molecule, which has only 3 atoms, it seems huge. If H2O is a big deal to calculate, you can imagine how difficult gramicidin S is. The largest protein known is Titin (a human adult has about 0.5 kg of Titin in their muscles) with [539,022](https://web.expasy.org/cgi-bin/protparam/protparam1?Q8WZ42@1-34350@) atoms (depending on which variant.) 


<!---
# OK, now what is a molecule
I will fill in more tonight. Stay tuned. 
--->
