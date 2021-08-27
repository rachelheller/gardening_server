from flask import Flask, request
from sqlalchemy import create_engine, Column, String, Integer, and_, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json

app = Flask(__name__)
app.config.from_envvar("APP_SETTINGS")

engine = create_engine(app.config["DATABASE_URL"], echo=True)

Base = declarative_base()


class Gardens(Base):
    __tablename__ = "gardens"

    id = Column(Integer, primary_key=True)
    name = Column(String(length=50))
    notes = Column(String(length=500))


class Plants(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True)
    name = Column(String(length=50))
    common_name = Column(String(length=50))
    category = Column(String(length=50))
    location = Column(String(length=50))
    year = Column(Integer)
    notes = Column(String(length=500))
    garden_id = Column(Integer, ForeignKey("gardens.id"))
    plant = relationship("Gardens", back_populates="plants")

Gardens.plants = relationship("Plants", order_by=Plants.id, back_populates="plant")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


@app.route("/gardens", methods=["GET"])
def all_gardens():
    results = session.query(Gardens).all()
    garden_list = []
    for result in results:
        garden = {"id": result.id, "name": result.name, "notes": result.notes}
        garden_list.append(garden)
    return json.dumps(garden_list)


@app.route("/gardens/create", methods=["POST"])
def create_garden():
    garden_name = request.form['name']
    garden_notes = request.form['notes']
    new_garden = Gardens(name=garden_name, notes=garden_notes)
    session.add(new_garden)
    session.commit()
    return ''


@app.route("/plants/create", methods=["POST"])
def create_plant():
    name = request.form["name"]
    common_name = request.form["common_name"]
    category = request.form["category"]
    location = request.form["location"]
    year = request.form["year"]
    notes = request.form["notes"] # how do I add the garden id as foreign key?
    new_plant = Plants(name=name, common_name=common_name, category=category, location=location, year=year, notes=notes)
    session.add(new_plant)
    session.commit()
    return ""


@app.route("/gardens/update/<int:garden_id>", methods=["POST"])
def update_garden(garden_id):
    name = request.form['name']
    notes = request.form['notes']
    session.query(Gardens).filter(Gardens.id == garden_id).update({Gardens.name: name, Gardens.notes: notes},
                                                                  synchronize_session=False)
    session.commit()
    return ""


@app.route("/plants/update/<int:plant_id>", methods=["POST"])
def update_plant(plant_id):
    name = request.form["name"]
    common_name = request.form["common_name"]
    category = request.form["category"]
    location = request.form["location"]
    year = request.form["year"]
    notes = request.form["notes"]
    session.query(Plants).filter(Plants.id == plant_id).update(
        {Plants.name: name, Plants.common_name: common_name, Plants.category: category, Plants.location: location,
         Plants.year: year, Plants.notes: notes}, synchronize_session=False)
    session.commit()
    return ""


@app.route("/gardens/search", methods=["POST"])
def search_gardens():
    garden_id = request.form["id"]
    results = session.query(Gardens).filter(Gardens.id == garden_id)
    garden_list = []
    for result in results:
        garden = {"id": result.id, "name": result.name, "notes": result.notes}
        garden_list.append(garden)
    return json.dumps(garden_list)


@app.route("/plants/search", methods=["POST"]) # how do I add garden_id to this?
def search_plants():
    plant_id = request.form["plant_id"]
    name = request.form["name"]
    common_name = request.form["common_name"]
    category = request.form["category"]
    location = request.form["location"]
    year = request.form["year"]
    notes = request.form["notes"]
    filters = []
    if plant_id != "":
        filters.append(Plants.id == plant_id)
    if name != "":
        filters.append(Plants.name.like(f"%{name}%"))
    if common_name != "":
        filters.append(Plants.common_name.like(f"%{common_name}%"))
    if category != "":
        filters.append(Plants.category == category)
    if location != "":
        filters.append(Plants.location == location)
    if year != "":
        filters.append(Plants.year == year)
    if notes != "":
        filters.append(Plants.notes.like(f"%{notes}%"))
    results = session.query(Plants).filter(and_(*filters))
    plant_list = []
    for result in results:
        plant = [result.id, result.name, result.common_name, result.category, result.location, result.year, result.notes]
        plant_list.append(plant)
    return json.dumps(plant_list)


@app.route("/plants/delete/<int:plant_id>", methods=["DELETE"])
def delete_plant(plant_id):
    result = session.query(Plants).filter(Plants.id == plant_id).one()
    session.delete(result)
    session.commit()
    return ""


@app.route("/gardens/delete/<int:garden_id>", methods=["DELETE"])
def delete_garden(garden_id):
    result = session.query(Gardens).filter(Gardens.id == garden_id).one()
    session.delete(result)
    session.commit()
    return ""
