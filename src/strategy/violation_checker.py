from miniapp import MiniApp
from strategy.req_before_use import check_req_before_use
from strategy.blanket_reqs import check_blanket_reqs
from strategy.compulsory_reqs import check_compulsory_reqs


class ViolationChecker:
    """
        Definition of ViolationChecker which is used to check compliance violations.

        -------
        Properties:
        - req_before_use: dict =>
            {
                'authorize_scope': authorize_scopes,
                'sensi_apis': sensi_apis,
                'violation_pages': violation_page
            }
        - blanket_reqs: dict =>
            {
                'authorize_scope': authorize_scopes,
                'sensi_apis': sensi_apis,
                'violation_pages': violation_page
            }
        - compulsory_reqs: list =>
            A list of violation{
                'page': page.page_path,
                'navigateToSuspiciousPage': False/True,
                'showSuspiciousModel': False/OptionalCase
            }
    """

    def __init__(self, miniapp: MiniApp):
        self.req_before_use = check_req_before_use(miniapp)
        self.blanket_reqs = check_blanket_reqs(miniapp)
        self.compulsory_reqs = check_compulsory_reqs(miniapp)
