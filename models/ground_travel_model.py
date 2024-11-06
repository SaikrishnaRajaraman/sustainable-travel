class GroundTravelModel:
    def __init__(self, id=None, travel_begin_date=None, travel_end_date=None, 
                 travel_expense_category=None, account=None, project_id=None, 
                 amount=0.0, carbon_emission=0.0):
        self.id = id
        self.travel_begin_date = travel_begin_date
        self.travel_end_date = travel_end_date
        self.travel_expense_category = travel_expense_category
        self.account = account
        self.project_id = project_id
        self.amount = amount
        self.carbon_emission = carbon_emission