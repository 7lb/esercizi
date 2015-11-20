# Create
### Aggiunta passi per la data corrente
POST /v1/days  
POST /v2/users/[user]/days
##### Parametri:
* steps: numero di passi effettuati

##### Ritorna:
201 Created:
```json
{
    "message": "Created",
    "day":  {
                "date": "2010-10-20",
                "steps": "100"
            },
    "uri": "http://localhost:5000/v1/days/2010-10-20"
}
```


# Retrieve
### Recupero passi per una data arbitraria
GET /v1/days/[data ISO 8601]  
GET /v2/users/[user]/days/[data ISO 8601]

##### Ritorna:
200 OK:
```json
{
    "message": "OK",
    "day":  {
                "date": "2010-10-20",
                "steps": "100"
            }
}
```

# Update
### Modifica passi per la data corrente
PUT /v1/days  
PUT /v2/users/[user]/days
##### Parametri:
* steps: numero di passi da aggiornare

##### Ritorna:
200 OK
```json
{
    "message": "OK",
    "day":  {
                "date": "2010-10-20",
                "steps": "100"
            },
    "uri": "http://localhost:5000/v1/days/2010-10-20"
}
```

# Delete
### Eliminazione passi per una data arbitraria
DELETE /v1/days/[data ISO 8601]  
DELETE /v2/users/[user]/days/[data ISO 8601]

##### Ritorna:
200 OK
```json
{
    "message": "OK",
    "day":  {
                "date": "2010-10-20",
                "steps": "100"
            }
}
```
