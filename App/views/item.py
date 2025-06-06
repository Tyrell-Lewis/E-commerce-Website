from flask import Blueprint, jsonify, render_template, request, flash, send_from_directory, redirect, url_for
from flask_login import login_required, current_user
import textwrap
from sqlalchemy import or_

from App.models import Customer, User, Product #,  Staff, Review
from App.controllers import (
    sell_item, get_all_items, get_item_by_id, get_all_items_by_type, get_favourite_products
)


item_views = Blueprint('item_views',
                        __name__,
                        template_folder='../templates')
'''
Page/Action Routes
'''

@item_views.route("/Home", methods=["GET"])
def index_page():
    flash(f"Message pop up works!")

    items = get_all_items()
    favourites = get_favourite_products(current_user.get_id())
    if favourites is not None:
        favourite_ids = set(f.productID for f in favourites)
    else:
        favourite_ids = []
    return render_template("landingPage.html", items=items, favourite_ids=favourite_ids)


@item_views.route("/product/<int:item_id>", methods=["GET"])
def product_page(item_id):
    

    item = get_item_by_id(item_id)
    return render_template("productPage.html", item=item)

@item_views.route("/allProducts", methods=["GET"])
@item_views.route("/allProducts/<string:c_type>", methods=["GET"])
def all_products_page(c_type=None):

    valid_types = ['t-shirt', 'pants', 'shoes', 'hoodies']
    
    if c_type in valid_types:
        items = get_all_items_by_type(c_type)
    else:
        items = get_all_items()
    return render_template("allProductsPage.html", items=items)



@item_views.route("/reduce_stock/<int:item_id>", methods=["GET"])
@login_required
def reduce_stock_action(item_id):
    sell_item(item_id, 2) #Replace 2 with the a varibale for quantity, which we get from some form or number picker.
    return redirect(request.referrer)


@item_views.route("/search", methods=["GET"])
def search():
    query = request.args.get('searchQuery', '').strip()

    if not query:
        return redirect (request.referrer)

    #Search working with page reload right now. How it works is that it gets the form query for searching, and uses what is there to match against all instances in the product model.
    search_filter = or_(
        Product.name.ilike(f'%{query}%'),
        Product.brand.ilike(f'%{query}%'),
        Product.colour.ilike(f'%{query}%'),
        Product.clothing_type.ilike(f'%{query}%'),
        #Product.description.ilike(f'%{query}%') Maybe have description but doesnt make senes right now, since the descriptions are all the same for testing.
    )

    results = Product.query.filter(search_filter).all()

    return render_template("landingPage.html", items=results)


@item_views.route("/live_search", methods=["GET"])
def live_search():
    query = request.args.get('searchQuery', '').strip()

    if not query:
        print("nothing")
        return jsonify([])

    #Search working with page reload right now. How it works is that it gets the form query for searching, and uses what is there to match against all instances in the product model.
    search_filter = or_(
        Product.name.ilike(f'%{query}%'),
        Product.brand.ilike(f'%{query}%'),
        Product.colour.ilike(f'%{query}%'),
        Product.clothing_type.ilike(f'%{query}%'),
        #Product.description.ilike(f'%{query}%') Maybe have description but doesnt make senes right now, since the descriptions are all the same for testing.
    )

    results = Product.query.filter(search_filter).all()

    products_json = [product.get_json() for product in results]

    if results:
        print("yes")
    else:
        print("no")

    return jsonify(products_json)