---
# Leave the homepage title empty to use the site title
title: ""
date: 2022-10-24
type: landing

design:
  # Default section spacing
  spacing: "6rem"

sections:
  - block: resume-biography-3
    content:
      # Choose a user profile to display (a folder name within `content/authors/`)
      username: admin
      text: ""
      # Show a call-to-action button under your biography? (optional)
      button:
        text: Download CV
        url: uploads/cv_stefan_gugler.pdf
    design:
      css_class: dark
      background:
        color: black
        image:
          # Add your image background to `assets/media/`.
          filename: stacked-peaks.svg
          filters:
            brightness: 1.0
          size: cover
          position: center
          parallax: false
  - block: markdown
    content:
      title: 'Research'
      subtitle: ''
      text: |
        I did my PhD at the Laboratory for Physical Chemistry (now: Institute of Molecular Physical Science) at ETH Zurich. I worked in the research group of [Prof. Markus Reiher](https://reiher.ethz.ch/). I developed procedures to apply methods from the field of machine learning and artificial intelligence to theoretical chemistry. My first paper applies Gaussian process regression and Bayesian sampling to dispersion interaction between organic compounds to yield more accurate results as well as streamline the pipeline of starting new reference calculations for compounds too dissimilar to the training set.

        Before, I worked at MIT under [Prof. Heather J. Kulik](https://hjkgrp.mit.edu/) for my Master thesis, on transition metal complexes for multifidelity machine learning. The work was [published](https://pubs.rsc.org/en/content/articlelanding/2020/me/c9me00069k) and won an MSDE award. Another [collaboration](https://pubs.acs.org/doi/10.1021/acs.iecr.8b04015) was published and a [follow up](https://pubs.aip.org/aip/jcp/article/157/18/184112/2842053) to my thesis.

        From 2013 to 2018 I studied Interdisciplinary Science at ETH Zurich with a major in Computational and Physical Chemistry.
  - block: collection
    id: papers
    content:
      title: Selected Publications
      filters:
        folders:
          - publication
        featured_only: true
    design:
      view: citation
  - block: markdown
    content:
      title: 'Recent Talks'
      subtitle: ''
      text: |
        - **06/2026** Generative exploration of chemical reaction networks. CNRS / Université de Lorraine, Nancy (invited)
        - **12/2025** How simple can you go? Machine learning molecular dynamics with minimal physical constraints. Pacifichem 2025, Honolulu
        - **10/2025** Machine learning and AI for the sciences: toward understanding. Latvian Institute of Organic Synthesis, Riga (invited)
        - **09/2025** Chemical reaction network exploration with diffusion probabilistic models. Young WATOC, Oslo; DTU Energy, Copenhagen (invited)
        - **08/2025** Generative computational chemistry: From reverse diffusion to XAI. University of Basel (invited)
        - **12/2024** Accelerating computational chemistry with machine learning. University of Freiburg (invited)

---
