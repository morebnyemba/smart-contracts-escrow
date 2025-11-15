"""
Custom signals for the transactions app.

These signals are used to notify other parts of the application about
important events in the transaction lifecycle.
"""
from django.dispatch import Signal

# Signal sent when a milestone is approved by the buyer
milestone_approved = Signal()

# Signal sent when a transaction is funded by the buyer
transaction_funded = Signal()

# Signal sent when a buyer requests revision on a milestone
revision_requested = Signal()
