superuser: 
username: marius
password: test123

groups: 
Admins (is_staff),
Manager,
Delivery Crew,
Customer

api mapping: 

/api/groups/manager/users
- POST(admins)
    * Can assign users to be added to the Manager group 

/api/groups/delivery-crew/users
- POST(managers)
    * Can assign users to be added to the Delivery Crew group

/api/register
- POST(any)
    * Anonymous users can register as a user and be added to the Customer group

/api/category
- GET(any authenticated), POST(admins)
    * GET: lists categories
    * POST: creates a category

/api/category/<id>
- GET(any authenticated)
    * GET: retrieves a specific category

/api/menu-items
- GET(any authenticated), POST(admins)
    * GET: lists menu items
        - filtering by category: ?category=<category>
        - ordering by field: ?ordering=<field>
        - pagination using ?perpage=<perpage>&page=<page>
    * POST: creates a menu item

/api/menu-items/<id>
- GET(any authenticated), PUT(managers), DELETE(admins)
    * GET: retrieves a specific menu item
    * PUT: used to update the featured flag for managers
    * DELETE: admins can delete a menu item

/api/cart
- GET(any authenticated), POST(all authenticated)
    * GET: Retrieves the current authenticated user's cart
    * POST: Creates a cart item (adds a menu item to the cart)

/api/orders
- GET(any authenticated), POST(all authenticated)
    * GET: lists orders for your user, except admins and managers who can see all orders
    * POST: adds an order
        - creates an order
        - creates order items for each cart item and assign them to the order
        - deletes the cart

/api/orders/<id>
- GET(any authenticated), PUT(managers, delivery crews)
    * GET: retrieves a specific order that is either assigned to the request user 
           if delivery crew or is the request user's own order. If admin or managers, see the order
    * PUT: delivery crew can update the status flag to true giving indication of order being delivered
           managers can assign delivery crew user to a specific order

/api/token/
- POST(any)
    * POST: can retrieve an access token and a refresh token based on username and password for a user.

/api/token/refresh/
- POST(any) 
    * POST: can retrieve a new access token and a refresh token  by using the refresh token thus refreshing the duration of the JWT