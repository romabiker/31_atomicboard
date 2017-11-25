import unittest
import sys
import time


from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


class BoardTests(unittest.TestCase):

    _new_ticket_title = 'Winter is close'
    _new_ticket_description = 'Check left amount of uranium'
    _page_title = 'AtomicBoard'
    _logout_locator = 'a[href="/logout/"]'
    _ticket_locator = 'div.js-ticket'
    _just_created_ticket_id_locator = \
    '.ticket__selected > div.panel-heading-no-padding > span.ticket_id'
    _add_ticket_block_locator = 'span.add-ticket-block_button'
    _input_ticket_title_locator = 'input.editable-has-buttons'
    _ticket_status_badge_locator = 'span.badge.ticket_status'
    _close_ticket_button_locator = \
    'div.change-status-form > div:nth-child(3) > button'
    _ticket_title_closed_locator = '.editable.ticket-title__resolved'
    _ticket_title_locator = \
        'div.js-ticket > div.panel-heading-no-padding > span.panel-heading_text'
    _ticket_description_locator = 'div.js-ticket_description_text'
    _select_ticket_cat_activator_locator = \
        '.js-ticket.ticket__selected > .ticket_description > div:nth-child(3) > span'
    _select_ticket_cat_locator = \
        '.js-ticket.ticket__selected > .ticket_description > div:nth-child(3) > form > div > select'
    _submit_ticket_cat_select_locator = \
        '.js-ticket.ticket__selected > div.panel-body.ticket_description > div:nth-child(3) > form > div > span > button.btn.btn-primary > span'
    _first_ticket_col_locator = \
        'div.row > span.col-md-10.js-board-wrapper > div > span:nth-child(1)'
    _second_ticket_col_locator = \
        'div.row > span.col-md-10.js-board-wrapper > div > span:nth-child(2)'
    _selected_ticket_from_first_col_locator = \
        'div.row > span.col-md-10.js-board-wrapper > div > span:nth-child(1) > div.js-ticket.ticket__selected'

    @classmethod
    def setUp(cls):
        cls.driver = webdriver.PhantomJS()
        cls.driver.set_window_size(1024, 768)
        cls.driver.implicitly_wait(30)
        cls.driver.get('http://atomicboard.devman.org/create_test_user/')
        try:
            button_create_user = cls.driver.find_element_by_tag_name('button')
            button_create_user.click()
        except NoSuchElementException:
            cls.tearDown()
            logging.error('Could not create new user')
            sys.exit(0)
        cls.driver.get('http://atomicboard.devman.org/')

    def test_site_is_displayed(self):
        self.assertEqual(self._page_title, self.driver.title)

    def test_page_is_logged(self):
        self.assertTrue(self.is_element_present(
            By.CSS_SELECTOR, self._logout_locator))

    def test_tickets_are_displayed(self):
        self.assertTrue(self.is_element_present(
            By.CSS_SELECTOR, self._ticket_locator))

    def test_ticket_create(self, added_tickets=1, time_out=5):
        driver = self.driver
        start_tickets_quantity = len(
            driver.find_elements_by_css_selector(self._ticket_locator))
        add_ticket_block = driver.find_element_by_css_selector(
                                  self._add_ticket_block_locator)
        add_ticket_block.click()
        input_ticket_block = driver.switch_to.active_element
        input_ticket_block.send_keys(self._new_ticket_title)
        input_ticket_block.submit()
        time.sleep(time_out)
        fin_tickets_quantity = len(
            driver.find_elements_by_css_selector(self._ticket_locator))
        self.assertEqual(fin_tickets_quantity,
            start_tickets_quantity + added_tickets)

    def test_ticket_close(self, time_out=5):
        ticket_status_badge = self.driver.find_element_by_css_selector(
                                          self._ticket_status_badge_locator)
        ticket_status_badge.click()
        time.sleep(time_out)
        close_ticket_button = self.driver.find_element_by_css_selector(
                                          self._close_ticket_button_locator)
        close_ticket_button.click()
        time.sleep(time_out)
        self.assertTrue(
            self.is_element_present(
                By.CSS_SELECTOR, self._ticket_title_closed_locator)
            )

    def test_ticket_title_redaction(self):
        driver = self.driver
        ticket_title_edit = driver.find_element_by_css_selector(
                                   self._ticket_title_locator)
        ticket_title_edit.click()
        ticket_title_input = driver.switch_to.active_element
        ticket_title_input.clear()
        ticket_title_input.send_keys(self._new_ticket_title)
        ticket_title_input.submit()
        self.assertEqual(self._new_ticket_title, ticket_title_edit.text)

    def test_ticket_description_redaction(self):
        driver = self.driver
        ticket_description = driver.find_element_by_css_selector(
            self._ticket_description_locator)
        ticket_description.click()
        input_ticket_description = driver.switch_to.active_element
        input_ticket_description.clear()
        input_ticket_description.send_keys(self._new_ticket_description)
        input_ticket_description.submit()
        self.assertEqual(self._new_ticket_description, ticket_description.text)

    def test_ticket_select_category(self,
            cat_exp_options=["проектирование", "производство"]):
        driver = self.driver
        cat_act_options = []
        select_ticket_cat_activator = \
            driver.find_element_by_css_selector(
                self._select_ticket_cat_activator_locator)
        select_ticket_cat_activator.click()
        select_ticket_cat = \
            Select(driver.find_element_by_css_selector(
                          self._select_ticket_cat_locator))
        self.assertEqual(len(cat_exp_options), len(select_ticket_cat.options))
        for option in select_ticket_cat.options:
            cat_act_options.append(option.text)
        self.assertListEqual(cat_exp_options, cat_act_options)
        self.assertEqual("проектирование",
                          select_ticket_cat.first_selected_option.text)
        select_ticket_cat.select_by_visible_text("производство")
        submit_ticket_cat_select = \
            driver.find_element_by_css_selector(
                self._submit_ticket_cat_select_locator)
        submit_ticket_cat_select.click()
        self.assertEqual("производство", select_ticket_cat_activator.text)

    def test_ticket_drag_and_drop(self,
            drag_and_drop_helper_js_file='drag_and_drop_helper.js',
            dragged_tickets=1):
        driver = self.driver
        first_ticket_col = \
            driver.find_element_by_css_selector(self._first_ticket_col_locator)
        second_ticket_col = \
            driver.find_element_by_css_selector(self._second_ticket_col_locator)
        tickets_in_first_col = len(
            first_ticket_col.find_elements_by_css_selector(self._ticket_locator))
        tickets_in_second_col = len(
            second_ticket_col.find_elements_by_css_selector(self._ticket_locator))
        with open(drag_and_drop_helper_js_file) as file_handler:
            drag_and_drop_js = file_handler.read()
        drag_and_drop_js_func_to_call = \
            '$("{what}").simulateDragDrop({{ dropTarget: "{target}"}});'.format(
                what=self._selected_ticket_from_first_col_locator,
                target=self._second_ticket_col_locator,)
        driver.execute_script(drag_and_drop_js + drag_and_drop_js_func_to_call)
        self.assertEqual(tickets_in_first_col - dragged_tickets,
            len(first_ticket_col.find_elements_by_css_selector(
                                                        self._ticket_locator)))
        self.assertEqual(tickets_in_second_col + dragged_tickets,
            len(second_ticket_col.find_elements_by_css_selector(
                                                        self._ticket_locator)))

    @classmethod
    def tearDown(cls):
        cls.driver.quit()

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True


if __name__ == '__main__':
    unittest.main(verbosity=2)
