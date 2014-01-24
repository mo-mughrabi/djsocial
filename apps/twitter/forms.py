from django import forms


class CreateOrderForm(forms.Form):
    """
    """
    order_types = (
        ('FollowUserForm', 'Follow user'),
        ('UnfollowUserForm', 'Unfollow user'),
        ('RetweetForm', 'Retweet'),
        ('FavForm', 'Favourite'),
        ('Hashtag_Form', 'Hashtag'),
    )
    order_type = forms.ChoiceField(choices=order_types)
