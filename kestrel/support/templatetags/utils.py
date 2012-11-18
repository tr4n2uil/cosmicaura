from django import template

register = template.Library()

def value( table, key ):
    return table.get( key, '' )
	
register.filter( 'value', value )

def limit( string, max ):
	max = int(max)
	if len( string ) > max:
		return string[ :max ] + ' ..'
	return string
	
register.filter( 'limit', limit )
