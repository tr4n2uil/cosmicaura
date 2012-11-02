from django import template

register = template.Library()

def value( table, key ):
    return table.get( key, '' )
	
register.filter( 'value', value )
