# API (backend)

Aplikacja posiada moduł API zbudowanego za pomocą Flaska.

## Swagger

Szczegółowe opisy poszczególnych metod/punktów końcowych zostały udostępnione za pomocą Swaggera: `/swagger`.

## Punkty końcowe

### Pobieranie danych

```http request title="Pobranie danych za pomocą modułu Google Scholar"
POST /gscholar/search
{
  "search_query": "python"
}
```

```http request title="Pobranie danych za pomocą modułu Elsevier API"
POST /scopus-api/search
{
  "search_query": "python"
}
```

```http request title="Pobranie danych za pomocą modułu bramki eksportu Scopusa"
POST /scopus-batch/search
{
  "search_query": "python"
}
```

### Dynamiczne wykresy

```http request title="Generowanie danych dla wykresu"
POST /dynamic-chart/data
```

```http request title="Eksport danych wykresu/tabeli w różnych formatach"
POST /dynamic-chart/export/{format}
```

### Filtry i opcje

```http request title="Pobranie dostępnych typów wykresów"
POST /filter-options/chart-type
```

```http request title="Pobranie listy kolumn dla wybranej tabeli"
POST /filter-options/columnList
```

```http request title="Pobranie dostępnych metod agregacji danych"
POST /filter-options/methods
```

```http request title="Pobranie dostępnych operatorów SQL"
POST /filter-options/operator
```

```http request title="Pobranie listy dostępnych tabel"
POST /filter-options/tableList
```

```http request title="Pobranie unikalnych wartości z danej kolumny"
POST /filter-options/uniqueValues
```

### Informacje systemowe

```http request title="Pobranie aktualnie używanej konfiguracji"
GET /system/config
```

```http request title="Szybki test statusu serwera"
GET /system/health
```

```http request title="Informacje o aktualnym środowisku"
GET /system/status
```


