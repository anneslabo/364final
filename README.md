This app will aid me in running my local banana bread business. I will connect to a weather API and assess dependent on weather if I should go to a farmers market or super market to get my groceries as farmers markets are cheaper. Then I will upload google sheets from my companies drive and load inventory currently stocked. Additionally I will have an order route where retailers can place weekly orders. Additionally based on total orders, my app will generate a list of groceries that I need to buy.



 **Ensure that your SI364final.py file has all the setup (app.config values, import statements, code to run the app if that file is run, etc) necessary to run the Flask application, and the application runs correctly on http://localhost:5000 (and the other routes you set up). Your main file must be called SI364final.py, but of course you may include other files if you need.**

 **A user should be able to load http://localhost:5000 and see the first page they ought to see on the application.**


 **Include navigation in base.html with links (using a href tags) that lead to every other page in the application that a user should be able to click on. (e.g. in the lecture examples from the Feb 9 lecture, like this )**

 **Ensure that all templates in the application inherit (using template inheritance, with extends) from base.html and include at least one additional block.

**Must use user authentication (which should be based on the code you were provided to do this e.g. in HW4)**

 **Must have data associated with a user and at least 2 routes besides logout that can only be seen by logged-in users.**
 #users are associated with order, orders

 **At least 3 model classes besides the User class.**
 #orders, inventory, Invoices

 **At least one one:many relationship that works properly built between 2 models.**

 b/w users and order


 **At least one many:many relationship that works properly built between 2 models.**

 bakers to orders

**Successfully save data to each table.**
examples with saving orders

 **Successfully query data from each of your models (so query at least one column, or all data, from every database table you have a model for) and use it to effect in the application (e.g. won't count if you make a query that has no effect on what you see, what is saved, or anything that happens in the app).**



 **At least one query of data using an .all() method and send the results of that query to a template.**
 #inventory query.all and in grocery

 **At least one query of data using a .filter_by(... and show the results of that query directly (e.g. by sending the results to a template) or indirectly (e.g. using the results of the query to make a request to an API or save other data to a table).**
 #used in almost every query

 **At least one helper function that is not a get_or_create function should be defined and invoked in the application.**
 #grocery list will be a helper function  

 **At least two get_or_create functions should be defined and invoked in the application (such that information can be saved without being duplicated / encountering errors).**
 (input one inventory item, input new flavor of bread )

 **At least one error handler for a 404 error and a corresponding template.**

 **At least one error handler for any other error (pick one -- 500? 403?) and a corresponding template.**

 **Include at least 4 template .html files in addition to the error handling template files.**
 #orders, register, login, index,

 **At least one Jinja template for loop and at least two Jinja template conditionals should occur amongst the templates.**
 #in order template

 **At least one request to a REST API that is based on data submitted in a WTForm OR data accessed in another way online (e.g. scraping with BeautifulSoup that does accord with other involved sites' Terms of Service, etc).**

 **Your application should use data from a REST API or other source such that the application processes the data in some way and saves some information that came from the source to the database (in some way).**
 #get weather info from weather API and use it to determine wherre to get groceries


**At least one WTForm that sends data with a GET request to a new page.**
From inventory you can go to the grocery list  



 **At least one WTForm that sends data with a POST request to the same page.** (NOT counting the login or registration forms provided for you in class.)
 inventory

**At least one WTForm that sends data with a POST request to a new page.** (NOT counting the login or registration forms provided for you in class.)

 orders

 **Include at least one way to update items saved in the database in the application (like in HW5).**
 update inventory after evaluating how many we made with current orders within the current orders


 **Include at least one way to delete items saved in the database in the application (also like in HW5).**
 You can delete inventory item

 **Include at least one use of redirect.**
 #example in the order route

 **Include at least two uses of url_for. (HINT: Likely you'll need to use this several times, really.)**

 **Have at least 5 view functions that are not included with the code we have provided. (But you may have more! Make sure you include ALL view functions in the app in the documentation and navigation as instructed above.)**

  (100 points) Include a use of an AJAX request in your application that accesses and displays useful (for use of your application) data.

 **(100 points) Create, run, and commit at least one migration.**

 **(100 points) Include file upload in your application and save/use the results of the file. (We did not explicitly learn this in class, but there is information available about it both online and in the Grinberg book.)**
 #used in the upload of inventory

 **(100 points) Deploy the application to the internet (Heroku) — only counts if it is up when we grade / you can show proof it is up at a URL and tell us what the URL is in the README. (Heroku deployment as we taught you is 100% free so this will not cost anything.)**

https://git.heroku.com/si364final18.git

 IIIIIIIIIIII (100 points) Implement user sign-in with OAuth (from any other service), and include that you need a specific-service account in the README, in the same section as the list of modules that must be installed.
