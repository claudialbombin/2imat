queries = {
    "pregunta1":
"""
db.películas.find(
    {},
    { _id: 0, país: 0, actores: 0, género: 0 }
)
""",
    "pregunta2":
"""
db.películas.find(
    { país: "USA" },
    { _id: 0, título: 1, director: 1, duración: 1, puntuación: 1 }
)
""",
    "pregunta3":
"""
db.películas.find(
    { país: "USA" },
    { _id: 0, título: 1, director: 1, duración: 1, puntuación: 1 }
).limit(4)
""",
    "pregunta4":
"""
db.películas.find(
    {},
    { _id: 0, título: 1, actores: 1, género: 1, puntuación: 1 }
).sort({ puntuación: -1 })
""",
    "pregunta5":
"""
db.películas.find(
    {},
    { _id: 0, título: 1, actores: 1, género: 1, puntuación: 1 }
).sort({ puntuación: -1 }).limit(1)
""",
    "pregunta6":
"""
db.películas.find(
    {
        $or: [
            { año: { $gt: 2015 } },
            { puntuación: { $gt: 8 } }
        ]
    },
    { _id: 0, título: 1, año: 1, puntuación: 1 }
).sort({ año: 1, puntuación: -1 })
""",
    "pregunta7":
"""
db.películas.find(
    {
        año: { $gte: 1970, $lte: 2000 }
    },
    { _id: 0 }
).sort({ año: 1 })
""",
    "pregunta8":
"""
db.películas.find(
    {
        duración: { $lt: 150 },
        puntuación: { $gte: 8 }
    },
    { _id: 0 }
).sort({ duración: 1, puntuación: -1 })
""",
    "pregunta9":
"""
db.películas.find(
    {
        director: { $in: ["George Lucas", "Quentin Tarantino", "Peter Jackson"] }
    },
    { _id: 0, título: 1, director: 1, año: 1, actores: 1 }
)
""",
    "pregunta10":
"""
db.películas.find(
    {
        $or: [
            { "actores.0": "Brad Pitt" },
            { "actores.0": "Johnny Depp" }
        ]
    },
    { _id: 0 }
).sort({ duración: -1 })
""",
    "pregunta11":
"""
db.películas.find(
    {
        secuela: { $exists: true },
        año: { $gt: 2010 }
    },
    { _id: 0 }
).sort({ año: 1 })
""",
    "pregunta12":
"""
db.películas.find(
    {
        actores: "Harrison Ford"
    },
    { _id: 0, título: 1, director: 1, actores: 1 }
)
""",
    "pregunta13":
"""
db.películas.updateMany(
    { director: "Peter Jackson" },
    { $set: { director: "Jackson, Peter" } }
)
""",
    "pregunta14":
"""
db.películas.updateMany(
    { país: "USA" },
    { $set: { país: "EEUU" } }
)
""",
    "pregunta15":
"""
db.películas.bulkWrite([
    {
        updateOne: {
            filter: { titulo: "8 apellidos vascos" },
            update: { $set: { secuela: "8 apellidos catalanes", puntuacion: 7 } }
        }
    },
    {
        deleteMany: {
            filter: { puntuacion: { $lte: 5.5 } }
        }
    },
    {
        replaceOne: {
            filter: { titulo: "El club de la lucha" },
            replacement: {
                titulo: "El club de los poetas muertos",
                pais: "EE. UU.",
                año: 1989,
                genero: ["Drama"],
                duracion: 128,
                presupuesto: 16.4,
                recaudacion: 235.86,
                puntuacion: 7.6,
                actores: ["Robin Williams", "Robert Sean Leonard"]
            }
        }
    }  // <-- No lleva coma aquí porque es el último elemento
])
""",
    "pregunta16_1":
"""
db.películas.find({ puntuación: { $gt: 7 } })
""",
    "pregunta16_2":
"""
db.películas.find({ puntuación: { $gt: 7 } }).explain("executionStats")
""",
    "pregunta16_3":
"""
db.películas.createIndex({ puntuación: -1 })
""",
    "pregunta16_4":
"""
db.películas.find({ puntuación: { $gt: 7 } }).explain("executionStats")
""",
    "pregunta17_1":
"""
db.películas.find({ presupuesto: { $gt: 100 } })
""",
    "pregunta17_2":
"""
db.películas.find({ presupuesto: { $gt: 100 } }).explain("executionStats")
""",
    "pregunta17_3":
"""
db.películas.createIndex({ presupuesto: 1 })
""",
    "pregunta17_4":
"""
db.películas.find({ presupuesto: { $gt: 100 } }).explain("executionStats")
""",
    "pregunta18":
"""
db.películas.createIndex({ género: "text" })
// Ver todas las películas de acción o comedia
db.películas.find(
    {
        $or: [
            { genero: { $regex: "acción", $options: "i" } },
            { genero: { $regex: "accion", $options: "i" } },
            { genero: { $regex: "comedia", $options: "i" } }
        ]
    },
    { _id: 0, titulo: 1, genero: 1, clasificacion: 1, puntuacion: 1 }
)
""",
    "pregunta19":
"""
db.películas.aggregate([
    {
        $group: {
            _id: "$clasificacion",
            totalRecaudado: { $sum: "$recaudacion" },
            mediaDuracion: { $avg: "$duracion" },
            menorPuntuacion: { $min: "$puntuacion" },
            mayorPresupuesto: { $max: "$presupuesto" }
        }
    },
    {
        $sort: { mediaDuracion: 1 }
    },
    {
        $project: {
            clasificacion: "$_id",
            _id: 0,
            totalRecaudado: { $round: ["$totalRecaudado", 2] },
            mediaDuracion: { $round: ["$mediaDuracion", 1] },
            menorPuntuacion: 1,
            mayorPresupuesto: 1
        }
    }
])
""",
    "pregunta20":
"""
db.películas.aggregate([
    {
        $group: {
            _id: "$pais",
            sumaPresupuestos: { $sum: "$presupuesto" },
            sumaRecaudaciones: { $sum: "$recaudacion" },
            mediaPuntuaciones: { $avg: "$puntuacion" },
            ultimoAño: { $max: "$año" },
            minimaDuracion: { $min: "$duracion" }
        }
    },
    {
        $sort: { ultimoAño: 1 }
    }
])
""",
    "pregunta21":
"""
db.películas.aggregate([
    {
        $match: {
            $or: [
                { productora: "Marvel Studios" },
                { puntuación: { $gt: 7 } }
            ]
        }
    },
    {
        $group: {
            _id: "$productora",
            añoMasAntiguo: { $min: "$año" },
            presupuestoMedio: { $avg: "$presupuesto" },
            puntuacionMedia: { $avg: "$puntuación" }
        }
    }
])
""",
    "pregunta22":
"""
db.películas.aggregate([
    {
        $match: {
            $or: [
                { presupuesto: { $lt: 100 } },
                { puntuacion: { $gt: 8 } }
            ]
        }
    },
    {
        $group: {
            _id: "$clasificacion",
            recaudacionMedia: { $avg: "$recaudacion" },
            mayorPresupuesto: { $max: "$presupuesto" },
            peorPuntuacion: { $min: "$puntuacion" },
            puntuacionMedia: { $avg: "$puntuacion" }
        }
    }
])
"""
}

queries_extra = {
    "extra1":
"""
db.películas.find(
    { país: "EEUU" },
    { _id: 0, título: 1, director: 1, duración: 1, puntuación: 1, recaudación: 1 }
).sort({ recaudación: -1 }).limit(1)
""",
    "extra2":
"""
db.películas.find(
    {},
    { _id: 0, título: 1, "actores.0": 1, género: 1, puntuación: 1 }
).sort({ puntuación: 1 }).limit(1)
""",
    "extra3":
"""
db.películas.find(
    {
        presupuesto: { $lte: 20 },
        recaudación: { $gte: 200 }
    },
    { _id: 0, título: 1, director: 1, presupuesto: 1, recaudación: 1 }
).sort({ recaudación: -1 })
""",
    "extra4":
"""
db.películas.find(
    {
        "actores.0": {
            $nin: ["Tom Holland", "Brad Pitt", "Johnny Depp"]
        }
    },
    { _id: 0 }
).sort({ duración: -1 })
""",
    "extra5":
"""
db.películas.find(
    {
        actores: { $regex: "ie", $options: "i" }
    },
    { _id: 0, título: 1, director: 1, actores: 1 }
)
""",
    "extra6":
"""
db.películas.find(
    {
        actores: { $regex: "Ford", $options: "i" }
    },
    { _id: 0, título: 1, director: 1, actores: 1 }
)
""",
    "extra7_1":
"""
db.películas.distinct("actores")
""",
    "extra7_2":
"""
db.películas.distinct("género")
""",
    "extra7_3":
"""
db.películas.distinct("año")
""",
    "extra8":
"""
db.películas.find(
    {
        $expr: { $eq: [{ $size: "$actores" }, 2] },
        puntuación: { $gt: 8 },
        duración: { $gt: 120 }
    },
    { _id: 0 }
).sort({ duración: 1 })
""",
    "extra9":
"""
db.películas.find(
    {
        $or: [
            { escritor: { $exists: false } },
            { escritor: "Stan Lee" }
        ],
        género: { $not: { $in: ["Drama"] } }
    },
    { _id: 0, título: 1, género: 1, año: 1, escritor: 1 }
).sort({ escritor: -1 })
""",
    "extra10":
"""
db.películas.countDocuments({
    recaudación: { $gt: 500 },
    puntuación: { $gt: 7.5 }
})
"""
}