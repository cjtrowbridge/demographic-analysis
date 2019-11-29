SELECT
	`PopulationID`,
	`Ethnicity`,
	`Foster Youth`,
	`Gender`,
	`Low Income`,
	`Disabilities`,
	`Transgender`,
	`Orientation`,
	`Veteran`,
	`Population 17`,
	`Population 18`,
	(`Population 18` - `Population 17`) as 'Population Change',
	`GPA 17`,
	`GPA 18`,
	round(`GPA 18` - `GPA 17`,2) as 'GPA Change',
	`First-Year Eng/Math Completion 17`,
	`First-Year Eng/Math Completion 18`,
	(`First-Year Eng/Math Completion 18` - `First-Year Eng/Math Completion 17`)||"%" as 'Eng/Math Change',
	`Course Success 17`,
	`Course Success 18`,
	(`Course Success 18` - `Course Success 17`)||"%" as 'Course Success Change',
	`Retention 17`,
	`Retention 18`,
	(`Retention 18` - `Retention 17`)||"%" as 'Retention Change'
	
FROM (
    SELECT
        Population.PopulationID,
        Ethnic as 'Ethnicity',
        FFY as 'Foster Youth',
        Gender,
        LowInc as 'Low Income',
        Disabilities,
        Transgender,
        SexOrient as 'Orientation',
        VeteranStatus as Veteran,
        Sum(Census.Fall2017) as 'Population 17',
        Sum(Census.Fall2018) as 'Population 18',
        round(avg(SuccessGPA.Fall2017),2) as 'GPA 17',
        round(avg(SuccessGPA.Fall2018),2) as 'GPA 18',
        (cast(
            round(
                avg(
                    ifnull(SuccessEngMath.Fall2018,0)
                ),0
            ) as int)
            ||"%"
        ) as 'First-Year Eng/Math Completion 17',
        (cast(
            round(
                avg(
                    ifnull(SuccessEngMath.Fall2018,0)
                ),0
            ) as int)
            ||"%"
        ) as 'First-Year Eng/Math Completion 18',
        (cast(
            round(
                avg(
                    ifnull(SuccessCourse.Fall2017,0)
                ),0
            ) as int)
            ||"%"
        ) as 'Course Success 17',
        (cast(
            round(
                avg(
                    ifnull(SuccessCourse.Fall2018,0)
                ),0
            ) as int)
            ||"%"
        ) as 'Course Success 18',
        (cast(
            round(
                avg(
                    ifnull(SuccessRetention.Fall2017,0)
                ),0)
            as int)
            ||"%"
        ) as 'Retention 17',
        (cast(
            round(
                avg(
                    ifnull(SuccessRetention.Fall2018,0)
                ),0)
            as int)
            ||"%"
        ) as 'Retention 18'
        
    FROM Population
    LEFT JOIN Census ON Census.PopulationID = Population.PopulationID
    LEFT JOIN SuccessGPA ON SuccessGPA.PopulationID = Population.PopulationID
    LEFT JOIN SuccessCourse ON SuccessCourse.PopulationID = Population.PopulationID
    LEFT JOIN SuccessRetention ON SuccessRetention.PopulationID = Population.PopulationID
    LEFT JOIN SuccessEngMath ON SuccessEngMath.PopulationID = Population.PopulationID

    WHERE
		SuccessGPA.Fall2017 IS NOT NULL AND
		SuccessGPA.Fall2018 IS NOT NULL /*AND
		SuccessCourse.Fall2017 IS NOT NULL AND
		SuccessCourse.Fall2018 IS NOT NULL AND
		SuccessRetention.Fall2017 IS NOT NULL AND
		SuccessRetention.Fall2018 IS NOT NULL*/

    GROUP BY Population.PopulationID
) x
WHERE 
	x.`Population 18` > 10 AND
	x.`Population 17` > 10
ORDER BY x.`Course Success 18` ASC