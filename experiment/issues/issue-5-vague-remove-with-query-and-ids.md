# remove() deleted the wrong thing

I called remove with a query and a list of ids at the same time because I wanted to be safe, and a document that has nothing to do with my query is gone. Same with update, it changed a document I didn't expect. Pretty sure this didn't used to happen. Can someone look at this?
