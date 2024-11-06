# **United Nations Official Records Website Project**
<img src="/un_project/un_app/static/images/un_seal.png" alt="UN Seal" width="350"/>

This project will eventually maybe become a replacement for our spreadsheets:

__Building Index:__
https://docs.google.com/spreadsheets/d/1UHE3NIoL8Cl78Vgs8Dlx_xnMDgdPvZiRhjuruxc6oF8/edit

__Finance Document__
https://docs.google.com/spreadsheets/d/1JdZUSav9DEh1bBfTcVBIFID3sLobqyq5nqLV7MwNyWo/edit?gid=1449818067#gid=1449818067


## Todo Roadmap
- **Balance Sheets**
    - [ ] Add Total Value of Total Cash & Cash Equivalents
    - [ ] Add Total Value of buildings
    - [ ] Manually order liquid assets (maybe create asset model with ordering field like item)
    - [ ] Move item calculations to the database rather then when the page is loaded to speed up loading times
    - [ ] Create liability tables
        - [ ] Add Mortgages section
        - [ ] Add Regular Loans section (Maybe rename?)
        - [ ] Add Total Liabilities
    - [ ] Create receivables & other assets tables
        - [ ] Add Receivables
        - [ ] Add Stock Investments
        - [ ] Lists Liabilities
    - [ ] Create total assets rundown (Total Cash & Cash Equivalents, Total Items, Total Territories, Other Assets & Liabilities = Total Assets)
    - [ ] Create loan tables for companies
        - [ ] Morgages, loans, and add Total Debt Assets
    - [ ] Create shareholders table for companies (Shareholder, %, diamond equivalent [total assets * %])
- **Evaluation Pages**
    - [ ] Must be logged in to see evaluation pages
    - [ ] Make evaluation success better (Instead of taking you to a different page)
    - [ ] Change building/item evaluations to be more like google sheets (ie. other evaluators listed, etc…)
        - [ ] All buildings/items listed
        - [ ] Other evaluator's evaluations listed
- **Misc.**
    - [ ] Sort buildings
        - [ ] Sort by nation
        - [ ] Sort by territory
        - [ ] Sort by year
        - [ ] Sort by building price
    - [ ] Create Graphs
        - [ ] Create historical records of nation/company assets (Total assets, liquid, items, buildings, other assets)
        - [ ] Individual nation/company graphs in their balance sheets
            - [ ] Total assets, liquid, items, buildings, other assets graphs over time
        - [ ] Pie chart of total assets of all nations (To show breakup of total world wealth)
        - [ ] Bar chart of current assets by nation 
            - [ ] Total assets, liquid, items, buildings, other assets graphs by nation
        - [ ] Line graph of assets over time by nation
            - [ ] Total assets, liquid, items, buildings, other assets graphs by nation by time
        - [ ] Size of nation stuff
            - [ ] Create historical records for size of nation data
            - [ ] Size of nation over time graph
                - [ ] Total territories, Main tarritories, far colonies, near colonies
    - [ ] Currency converter (ex: convert 42 emeralds and 58 copper to diamonds)
    - [ ] Item price calculator (Select items, see the price of them)
    - [ ] Architectural Styles stuff
    - [ ] Realty Commision?
    - [ ] Reids stuff
        - [ ] Credit score?
        - [ ] Amortiziation Scheule?
        - [ ] Inflation calculator?
        - [ ] Change base currence (ex: change all values to gold or netherite)?
    - [ ] Display map/maps?
        - [ ] Interactive map that shows buildings (Using coordinates)
            - [x] Convert coordinates to x, inverse z
            - [x] Color data points to each nation
            - [x] Add data for each building when data is clicked on
        - [ ] Somehow display historical/informative maps
    
