#include <iostream>
#include <fstream>
#include <string>
#include <regex>
#include <pugixml.hpp>
#include <iostream>

// To compile you need to link the pugixml lib
// g++ split_xml.cpp -l pugixml -o split_xml


const char* node_types[] =
{
    "null", "document", "element", "pcdata", "cdata", "comment", "pi", "declaration"
};

//string food = "Pizza";  // A food variable of type string
//string* ptr = &food; //ptr is a pointer to an item of type string and it is initialiaed to the address of food

struct simple_walker: pugi::xml_tree_walker
{
    
    virtual bool for_each(pugi::xml_node& node)
    {
        for (int i = 0; i < depth(); ++i) std::cout << "  ";
        std::string node_name = node.name();
        std::string protein_string = "protein";
        std::string mobidb_string = "MOBIDBLT";


        if (node_name == protein_string)
            std::cout << "\nFound protein id:" << node.attribute("id").value() << ":"  << "\n";
            /*
            pugi::xml_node child = node.first_child();
            std::string child_name = child.name();
            if (child_name == "match")
                std::string db_name = child.attribute("dbname").value();
                //std::cout << child.attribute("dbname").value();
                if (child.attribute("dbname").value() == mobidb_string)
                    std::cout << "\nFound mobidb entry : " << child.attribute("dbname").value();
            */

            // node should be a protein element
            for (pugi::xml_node child = node.first_child(); child; )
                {
                    // Get next child node before possibly deleting current child
                    pugi::xml_node next = child.next_sibling();
                    std::string child_name = child.name();
                    if (child_name == "match")
                        //std::string db_name = child.attribute("dbname").value();
                        //std::cout << "dbname: " << child.attribute("dbname").value() << "\n";
                        if(mobidb_string == child.attribute("dbname").value())
                            std::cout << "Found mobidb ";
                            for (pugi::xml_node mobi = child.first_child(); mobi; )
                                {
                                    pugi::xml_node next_mobi = mobi.next_sibling();
                                    std::cout << "start: " << mobi.attribute("start") << " end: " << mobi.attribute("end");
                                    mobi = next_mobi;
                                }
                    child = next;
                }
        return true;
    }
};


int main()
{
    pugi::xml_document doc;
    pugi::xml_parse_result result = doc.load_file("extras_part_test.xml");

    if (result){ 
        std::cout << "success";
    }else{
        std::cout << "fail";
    }
    std::cout << "Load result: " << result.description();

    //simple_walker walker;
    //doc.traverse(walker);

    pugi::xml_node root = doc.child("root");
    pugi::xml_node protein_root = doc.child("interproextra");

    for (pugi::xml_node protein = protein_root.first_child(); protein; protein = protein.next_sibling()) {
        std::string node_name = protein.name();
        if(node_name != "protein"){
            std::cout<< protein.name() << "not a protein\n" ;
        }
        else{
            std::string protein_id = protein.attribute("id").value();
            std::cout << "Protein id: " << protein_id << std::endl;
            //std::cout << "Child node name: " << child.name() << std::endl;
            
            //std::cout << "Child node text: " << child.child_value() << std::endl;
            //std::cout << "Child node attribute 'id': " << child.attribute("id").value() << std::endl;
            //std::cout << std::endl;
        }
    }

}










/* THIS WORKS
int main() {
    std::cout << "splitting xml 1";
    pugi::xml_document doc;

    // load file
    pugi::xml_parse_result result = doc.load_file("extras_part_test.xml");
    if (result){ 
        std::cout << "success";
    }else{
        std::cout << "fail";
    }
    std::cout << "Load result: " << result.description();

    // output children of the 'release' element
    pugi::xml_node tools = doc.child("interproextra").child("release");
    for (pugi::xml_node_iterator it = tools.begin(); it != tools.end(); ++it)
    {
        std::cout << "db name:";
        for (pugi::xml_attribute_iterator ait = it->attributes_begin(); ait != it->attributes_end(); ++ait)
        {
            std::cout << " " << ait->name() << "=" << ait->value();
        }
        std::cout << std::endl;
    }
    
}
*/
