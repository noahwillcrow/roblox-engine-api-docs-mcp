# Roblox API RAG

This project's objective is to provide an automatic, regularly-updated Docker image which provides a RAG API for all of the Roblox engine's APIs and the Creator Hub's extra documentation. The purpose is to serve as an easy-to-use, easy-to-share tool to empower LLM-based agents to have a strong knowledge-base of working with the Roblox engine, even outside of Roblox Studio itself. It should ultimately be shareable by giving developers a single docker image they need to spin up in a container locally (or wherever they'd like), and the version number should match the version of the Roblox game engine for that week (e.g. if the Roblox engine is on version 0.674, so is the image).

## How It Should Work

This project should use GitHub Actions to regularly (e.g. once a week) scrape the Roblox API dump and its Creator Hub source code, then intelligently load these into a vector DB, and finally expose that through some sort of JSON-based HTTP API that can be run locally and exposed through a single port on the container.

## Background Information to Know

- The Roblox game engine is typically updated weekly on Wednesdays (Pacific Time), so we should probably have this run at midnight on Thursday mornings (also Pacific time).
- This scraping work is essentially already done for us by a Roblox community all-star, Max. https://github.com/MaximumADHD/Roblox-Client-Tracker. At time of writing, its README was copied into [this file](./background/Roblox-Client-Tracker_README.md)
- A detailed research project was performed for investigating potential FOSS options for this; the [research write-up can be found here](./background/open-source-dependencies-research.md)
- The entire Roblox Creator Docs source files can be found at https://github.com/Roblox/creator-docs and are open-source; the README for this repo was copied into [this file](./background/creator-docs_README.md)

