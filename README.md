# Food manager

## assumptions

- spreadsheet is superior input interface
- my (yours) own recipe base is superior source of good food, users are not likely to pick new things

## goals

- simplify food logging and food planning
- suggest foods according to my own criteria
- provide analytics

## how

1. (done) input food plan using a spreadsheet, sync that spreadsheet with tasks so that it is easy to find on the phone
2. keep track of stash (too hard to keep motivation but that depends on usefullness)
3. input in spreadsheet is not constrained, so to get nutrition information
    1. find meal in my own recipe base
    2. if not try to get ingredients / similar recipes from my own base
    3. if not just get as much ingredients as possible from name then prompt the user to fill in details
        1. filling in should be easy and possible anytime
4. provide a way to define constraints and do search for meal plan, but only 2-3 days ahead, doing more does not really make sense because life is chaotic
    1. meal plan is synced with spreadsheet and tasks so it's very easy to edit
5. automatically create shopping lists
6. suggest / automatically create meal plans using exhaustive search for now