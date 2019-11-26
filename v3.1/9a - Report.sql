SELECT
    Population.PopulationID,
    Disabilities,
    Ethnic as 'Ethnicity',
    FFY as 'Foster Youth',
    Gender,
    LowInc as 'Low Income',
    Transgender,
    SexOrient as 'Orientation',
    VeteranStatus as Veteran,
    Sum(Census.Fall2018) as 'Population Size',
    round(avg(SuccessGPA.Fall2018),2) as 'Latest GPA',
    (cast(
        round(
            avg(
                SuccessEngMath.Fall2018
            ),0
        ) as int)
        ||"%"
    ) as 'First-Year Eng/Math Completion',
    (cast(
        round(
            avg(
                SuccessCourse.Fall2018
            ),0
        ) as int)
        ||"%"
    ) as 'Course Success',
    (cast(
        round(
            avg(
                SuccessRetention.Fall2018
            ),0)
        as int)
        ||"%"
    ) as Retention
    
FROM Population
INNER JOIN Census ON Census.PopulationID = Population.PopulationID
INNER JOIN SuccessGPA ON SuccessGPA.PopulationID = Population.PopulationID
INNER JOIN SuccessCourse ON SuccessCourse.PopulationID = Population.PopulationID
INNER JOIN SuccessRetention ON SuccessRetention.PopulationID = Population.PopulationID
INNER JOIN SuccessEngMath ON SuccessEngMath.PopulationID = Population.PopulationID

GROUP BY Population.PopulationID

HAVING
    'Population Size' > 10 AND
    Retention IS NOT NULL AND
    'Latest GPA' IS NOT NULL AND
    'Course Success' IS NOT NULL AND
    'First-Year Eng/Math Completion' IS NOT NULL
