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
I used the word 'neural winter' in the podcast yet in the literature you would rather read about the 'AI winter'. I was introduced to the concept with the first term, but it means the same: A period starting from the 70ies and peaking in early 90ies where funding for AI was sparse and people were rather pessimistic about progress in AI. At latest in 2012, machine learning and AI is back on track with successful application of neural nets and deep learning for a host of problems.
<!---
<NEURAL WINTER HISTOGRAM figure>
https://en.wikipedia.org/wiki/Timeline_of_artificial_intelligence
--->

## Early Computational Chemistry
John Pople was one of the fathers of computational chemistry proper with the developement of the quantum chemical software Gaussian. He won the [Nobel Prize in 1998](https://www.nobelprize.org/prizes/chemistry/1998/pople/facts/) and he died in 2004, aged 78.
![Pople in all his glory](/images/school-of-batman/pople.jpg)

<!---
# OK, now what is a molecule
I will fill in more tonight. Stay tuned. 
--->
