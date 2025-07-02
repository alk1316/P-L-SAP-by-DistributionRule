# P&L SAP by DistributionRule

Este proyecto es una aplicación desarrollada en **Python** con **Panel** para visualizar reportes de **Ganancias y Pérdidas (P&L)** utilizando los datos financieros extraídos desde **SAP Business One**.

La herramienta permite realizar un análisis dinámico de resultados por **Distribución Analítica (Distribution Rule)**, con la posibilidad de ver la información **mensual, trimestral o anual**, y con una estructura jerárquica tipo árbol (cuentas agrupadas por niveles contables).

---

## 🚀 Funcionalidades principales

- 🧾 **Visualización jerárquica** de cuentas contables (Nivel 1, 2 y 3).
- 📅 **Análisis por periodo**: mensual, trimestral y anual.
- 🧮 **Totales dinámicos** por cada grupo contable.
- 🔍 **Filtrado por dimensión** (Distribution Rule).
- 📊 **Ganancia/Pérdida final** calculada automáticamente.
- 💡 Visual elegante y compacta, optimizada para lectura financiera.

---


---

## 🔧 Requisitos

- Python 3.8 o superior
- Panel
- Pandas

## Como ejecutar
panel serve plan_cuentas_panel.py --autoreload


## 📥 Query SAP HANA para extraer modelo financiero

```sql
SELECT 
    T0."CatId"
    , T0."TemplateId"
    , T0."Name"
    , T0."Levels"
    , T0."FatherNum"
    , T0."Active"
    , T1."CatId"
    , T1."TemplateId"
    , T1."AcctCode"
    , T2."ActId"
    , T2."AcctName"
FROM OFRC T0 
LEFT JOIN FRC1 T1 ON T0."TemplateId" =T1."TemplateId" AND T0."CatId"=T1."CatId" 
LEFT JOIN OACT T2 ON T1."AcctCode" = T2."AcctCode" 
WHERE T0."TemplateId" =-97 
ORDER BY T0."CatId", T0."Levels"
```

## 📥 Query SAP HANA para extraer movimientos contables por Dimension 1

Este query extrae todos los movimientos contables de resultado por Dimension1 con su distribucion de centro de costo y normas de reparto

```sql
SELECT  DISTINCT 

T0."TransId", T4."OcrCode", 
       T4."OcrName", 
       T5."PrcCode",  
       T6."PrcName", -- Ajuste aquí
       T2."AcctCode", T2."AcctName", 

case when T0."TransType"='30' then
cast(T0."TransId" as varchar(50))
else

      cast( T0."Ref1" as varchar(50)) end  as "DocNum",
       T0."FolioNum", T0."RefDate", 
       T0."TaxDate", T0."DueDate", 
       CASE WHEN T3."CardCode" IS NULL THEN 'NA' ELSE T3."CardCode" END AS "CardCode" , T3."CardName", 
       (CASE 
          WHEN T2."ActType" = 'I' THEN 
            (CASE 
               WHEN T1."Debit" != 0 THEN T1."Debit"* -1  
               ELSE T1."Credit" 
             END) * T5."PrcAmount"/100
          WHEN T2."ActType" = 'E' THEN 
          (  (CASE 
               WHEN T1."Debit" != 0 THEN T1."Debit" 
               ELSE T1."Credit" * -1 
             END) *(-1)* T5."PrcAmount")/100
          ELSE 0
        END) AS "Total",
T1."Line_ID"
FROM OJDT T0  
INNER JOIN JDT1 T1 ON T0."TransId" = T1."TransId" 
INNER JOIN OACT T2 ON T1."Account" = T2."AcctCode" 
left JOIN OCRD T3 ON 
  (SELECT MAX(T10."ShortName") 
   FROM JDT1 T10  
   INNER JOIN OACT T11 ON T10."Account" = T11."AcctCode" 
   WHERE T11."LocManTran" = 'Y' AND T10."TransId" = T0."TransId") = T3."CardCode" 
LEFT JOIN OOCR T4 ON T1."ProfitCode" = T4."OcrCode" 
LEFT JOIN OCR1 T5 ON 
    T4."OcrCode" = T5."OcrCode" 
    AND T1."RefDate" >= T5."ValidFrom" 
    AND (T5."ValidTo" IS NULL OR T1."RefDate" <= T5."ValidTo")

LEFT JOIN OPRC T6 ON T5."PrcCode" = T6."PrcCode" -- Nueva unión para traer el nombre
WHERE T1."RefDate" >= '20250101' 
  AND T1."RefDate" <= '20251201' 
  AND T2."ActType" != 'N'
--AND T0."U_OK1_IFRS"!='L'
AND T4."Active"='Y'

```


