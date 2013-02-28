/**
 *	@header object
 *	@desc utilities for libobject interface
 *
 *	@author	Vibhaj Rajan <vibhaj8@gmail.com>
**/

#ifndef __OBJECT_H__
#define __OBJECT_H__

#include <iostream>
#include <sstream>
#include "univcont.h"

typedef JAD::UniversalContainer Object;

inline void json_encode_out(const Object &obj, std::ostream& out = std::cout){
	JAD::Buffer* buf = JAD::uc_encode_json(obj);
	JAD::write_from_buffer(buf, out);
    delete buf;
}

inline std::string json_encode(const Object &obj){
	ostringstream sout;
	json_encode_out(obj, sout);
	return sout.str();
}

#endif

