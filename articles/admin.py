from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _

from .models import Article, Tag, Scope


class RelationshipInlineFormset(BaseInlineFormSet):
    def clean(self):
        main_scopes_count = 0
        for form in self.forms:
            if form.cleaned_data.get('is_main'):
                main_scopes_count += 1
        if main_scopes_count != 1:
            raise ValidationError(_('There must be one and only one main scope.'))
        return super().clean()


class ScopeInline(admin.TabularInline):
    model = Scope
    formset = RelationshipInlineFormset


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [
        ScopeInline,
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        main_scopes = obj.scopes.filter(is_main=True)
        if not main_scopes.exists():
            main_scope = obj.scopes.first()
            if main_scope:
                main_scope.is_main = True
                main_scope.save()
        else:
            obj.scopes.exclude(id__in=main_scopes.values_list('id', flat=True)).update(is_main=False)