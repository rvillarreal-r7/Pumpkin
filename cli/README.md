### Click Docs for Pumpkin
I'm basically setting this up like so. 

main imports cli_common and then kicks off the cli by using the func cli()

In the cli_common cli func 
we are basically using this as a way to create a click object for each file in this dir I believe. 
you would just use the import section to be like import search.py as search_mod and then include the object into the CommandCollection sources