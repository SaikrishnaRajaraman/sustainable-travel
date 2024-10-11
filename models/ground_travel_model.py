class GroundTravelModel:
    def __init__(self, id,travel_begin_date,travel_end_date,travel_expense_category,account,project_id, amount,carbon_emission):
        self.id = id
        self.travel_begin_date = travel_begin_date
        self.travel_end_date = travel_end_date
        self.travel_expense_category = travel_expense_category
        self.account = account
        self.project_id = project_id
        self.amount = amount
        self.carbon_emission = carbon_emission