from django.core.exceptions import ImproperlyConfigured
from django.template.base import Library, TemplateSyntaxError, Node
from django.template.loader import get_template

register = Library()


class UpdownIsUserVoted(Node):
    def __init__(self, instance, field_name, template_name):
        vars = locals()
        del vars['self']
        self.__dict__.update(vars)

    def render(self, context):
        user = context.get('user')

        if not user:
            raise ImproperlyConfigured("Auth context processor must be enabled for successful work of tag 'voted'")

        instance = self.instance.resolve(context)
        field_name = self.field_name.resolve(context)
        template_name = self.template_name.resolve(context)

        rating_field = getattr(instance, field_name)
        if rating_field.check_user_voted(user):
            return unicode(rating_field.get_difference())
        else:
            template = get_template(template_name)
            output = template.render(context)
            return output


@register.tag('voted')
def updown_user_voted(parser, token):
    """
    {% voted instance on field include template %}
    """
    bits = token.split_contents()
    if len(bits) < 6:
        raise TemplateSyntaxError(
            "'voted' tag must be in form {% voted instance_var on field_name include template_var %}"
        )

    tag, instance, on, field_name, include, template_name = bits

    instance = parser.compile_filter(instance)
    field_name = parser.compile_filter(field_name)
    template_name = parser.compile_filter(template_name)

    return UpdownIsUserVoted(instance, field_name, template_name)

