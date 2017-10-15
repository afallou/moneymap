moneymap
========

This is the code used for a project done as part of class [CS224w](http://web.stanford.edu/class/cs224w/) "Analysis of Networks" in Fall 2014.

The aim of the project was to understand the influence of money in U.S. politics through a graphical analysis of campaign finance data (who donates to whom) and Congress voting data (how members of Congress on particular laws).

See the report folder for [a more complete report](./report/analysis-political-network.pdf) on the work

### Files ###
fetching_data.py - fetches data from the sunlight foundation API

parse_votes.py - parses the vote data to create data structures for voting and calculates edge weights

impact_organization.py - analyzes impact of organizations

impact_graph.py - the high level impact analysis

contributions.json - json of all contributions to the 2012 campaign

graph_display.html - d3 visualization of the graphs

recipients_graph_good_and_bad_reps.json - graph of representatives

centrality_measure.py - calculates our centrality

balance.py - calculates balance of graph

scrape_positions.py - web scraper
