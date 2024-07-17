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

    // The main file is too big and will run out of memory
    //pugi::xml_parse_result result = doc.load_file("/Volumes/My Passport 3/downloads/extra.xml");

    if (result){ 
        //std::cout << "success";
    }else{
        //std::cout << "fail";
    }
    std::cout << "Load result: " << result.description();

    //simple_walker walker;
    //doc.traverse(walker);
    int record_count = 0;
    pugi::xml_node root = doc.child("root");
    pugi::xml_node protein_root = doc.child("interproextra");

    for (pugi::xml_node protein = protein_root.first_child(); protein; protein = protein.next_sibling()) {
        std::string node_name = protein.name();
        if(node_name != "protein"){
            //std::cout<< protein.name() << "not a protein" << std::endl ;
        }
        else{
            std::string protein_id = protein.attribute("id").value();
            //std::cout << "Protein id: " << protein_id << std::endl;

            // protein is now node with children whcih are matches
            for (pugi::xml_node match = protein.first_child(); match; match = match.next_sibling()) {
                std::string mobidb_match = "MOBIDBLT";
                //std::cout << match.name() << match.attribute("dbname").value() << std::endl;
                if(match.attribute("dbname").value() == mobidb_match){
                    // match is now a mobidb attribute
                    for (pugi::xml_node match_detail = match.first_child(); match_detail; match_detail = match_detail.next_sibling()) {
                        record_count +=1;
                        std::cout << record_count << "|" << protein_id << "|DISORDER|" << match_detail.attribute("sequence-feature").value() << "|" << match_detail.attribute("start").value() << "|" << match_detail.attribute("end").value() << std::endl;
                    }
                }
            }

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
