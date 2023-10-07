from enum import Enum


class Waves(Enum):
    """
    22 Elite male
    17 Elite female
    There are some holes, so either some runners did not show up or there was spare capacity.
    https://runsignup.com/Race/EmpireStateBuildingRunUp/Page-4
    https://runsignup.com/Race/EmpireStateBuildingRunUp/Page-5
    I guessed who went on which category, based on the BIB numbers I saw that day
    """
    EliteMen = [1, 25]
    EliteWomen = [26, 49]
    Specialty = [50, 99]
    Sponsors = [100, 199]
    """
    The date people applied for the lottery?
    General Lottery Open: 7/17 9AM- 7/28 11:59PM
    General Lottery Draw Date: 8/1
    """
    Green = [200, 299]
    Orange = [300, 399]
    Grey = [400, 499]
    Gold = [500, 599]
    Black = [600, 699]
