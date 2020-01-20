import asyncio

import sanic
from bson import ObjectId
from sanic_jinja2 import SanicJinja2
import pymongo

loop = asyncio.get_event_loop_policy().new_event_loop()
app = sanic.Sanic()
jinja = SanicJinja2(app)
mdb = pymongo.MongoClient()
a73online = mdb.get_database("una").get_collection("a73online")


@app.get("/")
async def index(request):
    return jinja.render(
        "index.jinja2",
        request,
        articles=list(a73online.find(sort=[("date", pymongo.DESCENDING)])),
    )


@app.get("/article/<id>")
async def article(request, id):
    return jinja.render(
        "article.jinja2", request, article=a73online.find_one({"_id": ObjectId(id)})
    )


app.static("static/", "static/")

if __name__ == "__main__":
    app.run()
