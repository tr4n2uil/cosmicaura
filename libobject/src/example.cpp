#include <iostream>
using namespace std;

#include "object.h"

void print_person(Object& obj)
{
  string name = obj["name"];
  string age = obj["age"];
  char sex = obj["sex"];
  
  cout << name << '\t' << sex << '\t' << age << endl;
}

/*
  A simple example that declares a record holding the personal records
  of a soldier and his family.
 */
int main(int argc, char** argv)
{
  try {
    Object soldier;

    //Note all the different types of primitives that can be assigned to
    //arbitrary keys.
    soldier["name"] = "Kansas Smith";
    soldier["age"] = 23;
    soldier["officer"] = false;
    soldier["serial"] = 789456;
    soldier["sex"] = "M";
    soldier["wage"] = 25.75;
    
    //We can easily nest UniversalContainers
    soldier["spouse"]["name"] = "Sue Smith";
    soldier["spouse"]["sex"] = "F";
    soldier["spouse"]["age"] = "Won't Say";
    
    //Or have a container act as an array.
    //In this case, the key "dependants" maps to a UniversalContainer that is an array of
    //other UniversalContainers, which in turn have their own keys.
    soldier["dependants"][0]["name"] = "Joe Smith";
    soldier["dependants"][0]["age"] = 3;
    soldier["dependants"][0]["sex"] = "M";
    soldier["dependants"][1]["name"] = "Ann Smith";
    soldier["dependants"][1]["age"] = 1;
    soldier["dependants"][1]["sex"] = "F";
    soldier["dependants"][2]["name"] = "On the way";
    
    cout << "NAME" << "\t\t" << "SEX" << "\t" << "AGE" << endl;
    print_person(soldier);
    
    //A UC can be a map between strings and other UCs.
    print_person(soldier["spouse"]);

    //We can loop through the array of dependants
    for (unsigned i = 0; i < soldier["dependants"].size(); i++)
      print_person(soldier["dependants"][i]);
    
    //Here is an example of using dot notation to get at nested elements
    cout << "The litte girls name is " << 
      (string)soldier["dependants.1.name"] << endl;
    
    //Here we show how a container may be cast as the type it is holding
    double combat_pay = (double)soldier["wage"] + 5.35;
    cout << "Combat pay is " << combat_pay << endl;

    //This is essential what the print statement does,
    //we show it here as an example of using the serializer code.
    cout << json_encode(soldier) << endl;

  }
  //We shouldn't ever be here, but if we are, the exception will contain
  //key/value pairs describing what went wrong.
  catch(Object uce) {
    cout << "An exception was thrown." << endl;
    print(uce);
  }
}
