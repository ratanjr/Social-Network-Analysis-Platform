LOAD CSV FROM 'file:///facebook_combined.txt' AS line
WITH split(line[0], ' ') AS parts
WITH parts[0] AS sourceStr, parts[1] AS targetStr
WHERE sourceStr IS NOT NULL AND targetStr IS NOT NULL
WITH toInteger(sourceStr) AS source, toInteger(targetStr) AS target
MERGE (s:Node {id: source})
MERGE (t:Node {id: target})
MERGE (s)-[:CONNECTED_TO]->(t);