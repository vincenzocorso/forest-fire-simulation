class RainFactorCalculator:
    @staticmethod
    def compute_rain_factor(cell, state):
        """
            Computer the rain component:
            - if it's raining and the cell is burning then decrease the burning state
            - if it's raining and the cell is not burning (nor burned) then decrease temporarily the spread component (sc_deficit)
            - if it isn't raining and the cell is not burning then halves sc_deficit (soil is drying)
        """
        if cell.rain > 0:
            if state > 0:
                return state * RainFactorCalculator.rain_suppression(cell)
            else:
                cell.rain_deficit = RainFactorCalculator.rain_sc_reduction(cell)
                return state
        else:
            update_deficit = cell.rain_deficit * 0.5
            if update_deficit < 0.01:
                update_deficit = 0
            cell.rain_deficit = update_deficit
            return state

    @staticmethod
    def rain_suppression(cell):
        return 1 - max(min(0.8, (0.0242424242424 * cell.rain) - 0.0484848484848), 0)

    @staticmethod
    def rain_sc_reduction(cell):
        return max(min(0.8, 0.12 * cell.rain), 0)
