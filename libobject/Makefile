include Makesetup.inc

CPP_FILES := $(wildcard src/*.cpp)
OBJ_FILES := $(addprefix obj/,$(notdir $(CPP_FILES:.cpp=.o)))

all: bin/example

bin/example: lib/libobject.a obj/example.o
	$(CXX) $(LD_FLAGS) -L ./lib -o $@ obj/example.o -lobject

lib/libobject.a : obj/ucontainer.o obj/buffer.o obj/buffer_util.o \
obj/ucoder_ini.o obj/ucoder_bin.o obj/string_util.o obj/uc_web.o \
obj/ucio.o obj/ucoder_json.o obj/buffer_curl.o obj/uccontract.o \
obj/ucdb.o $(OPT_FILES)
	rm -f lib/libobject.a
	$(STATICLIB) $@ $^

obj/%.o: src/%.cpp
	$(CXX) $(CXX_FLAGS) -c -o $@ $^

src/ucoder_json.cpp : src/json_parser.lex
	cd src; flex -o ucoder_json.cpp json_parser.lex

install:
	install -m644 -o root -g wheel src/*.h $(INSTALLDIR)/include
	install -m644 -o root -g wheel lib/*.a $(INSTALLDIR)/lib

uninstall:
	rm -f $(INSTALLDIR)/include/buffer.h
	rm -f $(INSTALLDIR)/include/stl_util.h
	rm -f $(INSTALLDIR)/include/string_util.h 
	rm -f $(INSTALLDIR)/include/uc_web.h 
	rm -f $(INSTALLDIR)/include/ucio.h 
	rm -f $(INSTALLDIR)/include/ucdb.h 
	rm -f $(INSTALLDIR)/include/ucmysql.h
	rm -f $(INSTALLDIR)/include/ucontainer.h 
	rm -f $(INSTALLDIR)/include/ucsqlite.h 
	rm -f $(INSTALLDIR)/include/univcont.h        
	rm -f $(INSTALLDIR)/lib/libobject.a

clean :
	rm -f obj/*.o
	rm -f lib/*.a
	rm -f bin/example

