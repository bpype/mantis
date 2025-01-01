#!/bin/bash
# A tool for adding the boilerplate code for adding a new node to the tree.

parentclass=""
nodefile=""
cnodefile=""
classfile=""
icon=""


#                     title: name           menu: name,      H  W  menu size    pairs of tag,description,  trick to swap stdout and stderr
nodetype=$(whiptail --title "add_node.sh" --menu "Node Type" 25 78 16 "xForm" "" "Link" "" "Utility" "" "Math" "" 3>&2 2>&1 1>&3)
if [[ $nodetype == "" ]]; then
    echo "Cancelled."
else
    case $nodetype in
      Link)
        nodefile="link_definitions.py"
        parentclass="LinkNode"
        cnodefile="link_containers.py"
        icon="CONSTRAINT_BONE"
        ;;
       
      xForm)
        nodefile="xForm_definitions.py"
        cnodefile="xForm_containers.py"
        parentclass="xFormNode"
        icon="EMPTY_AXIS"
        ;;
        
      Utility)
        nodefile="nodes_generic.py"
        cnodefile="misc_containers.py"
        parentclass="MantisNode"
        icon="NODE"
        ;;

      Math)
        nodefile="math_definitions.py"
        cnodefile="math_containers.py"
        parentclass="MantisNode"
        icon="NODE"
        ;;
    esac


    cancelled=0

    check_cancelled() {
        if [[ $cancelled == "1" ]]; then
            echo "Cancelled."
            exit
        fi
    }
    
    
    #read class_name
    class_name=$(whiptail --inputbox "Name of new node?" 8 39 "" --title "add_node.sh" 3>&1 1>&2 2>&3)
    cancelled=$?; check_cancelled
    whiptail --title "add_node.sh" --msgbox \
    "Node class will be named $nodetype$class_name$n_text with bl_idname $nodetype$class_name" 8 78
    bl_label=$(whiptail --title "add_node.sh" --inputbox "UI Label new node class?" 8 39 "" 3>&1 1>&2 2>&3)
    cancelled=$?; check_cancelled
    docstring=$(whiptail --title "add_node.sh" --inputbox "Docstring for new node class?" 8 39 "" 3>&1 1>&2 2>&3)
    cancelled=$?; check_cancelled
    
    # TODO: I would like to be able to define the number of inputs and their names
    #        and the script will add them to the file
    #        it should also give me the option to choose socket type and such
    #       Utility nodes would also give the option of adding outputs.
    
    declare -i num_inputs="0"
    declare -i num_outputs="0"
    
    if [[ $nodetype == 'Link' || $nodetype == 'Utility' ]]; then
        choice=$(whiptail --title "add_node.sh"\
          --inputbox "Number of inputs? Note: This number is in addition to the default inputs." 8 39 "0" 3>&1 1>&2 2>&3)
        if [[ "$choice" -eq "$choice" ]]; then
            num_inputs=$choice
        else
            echo "Error, must be a number"
            cancelled=1
        fi
        cancelled=$?; check_cancelled
    
    elif [[ $nodetype == 'Utility' ]]; then
        choice=$(whiptail --title "add_node.sh"\
          --inputbox "Number of outputs?" 8 39 "0" 3>&1 1>&2 2>&3)
        if [[ "$choice" -eq "$choice" ]]; then
            num_outputs=$choice
        else
            echo "Error, must be a number"
            cancelled=1
        fi
        cancelled=$?; check_cancelled
    elif [[ $nodetype == 'Math' ]]; then

        choice=$(whiptail --title "add_node.sh"\
          --inputbox "Number of inputs?" 8 39 "0" 3>&1 1>&2 2>&3)
        if [[ "$choice" -eq "$choice" ]]; then
            num_inputs=$choice
        else
            echo "Error, must be a number"
            cancelled=1
        fi
        cancelled=$?; check_cancelled

        choice=$(whiptail --title "add_node.sh"\
          --inputbox "Number of outputs?" 8 39 "0" 3>&1 1>&2 2>&3)
        if [[ "$choice" -eq "$choice" ]]; then
            num_outputs=$choice
        else
            echo "Error, must be a number"
            cancelled=1
        fi
        cancelled=$?; check_cancelled
    else
        num_inputs=0
    fi
    


    
    if [[ $nodetype == 'Utility' && $num_inputs == "0" && $num_outputs == "0" ]]; then
        echo "Error. The node must have at least one socket."
        exit
    fi
    # now, set a flag if this is a utility and has no inputs but has outputs
    isinput=0
    if [[ $nodetype == 'Utility' && $num_inputs == "0" && $num_outputs -gt 0 ]]; then
        isinput=1
    fi
    
    
    
    
    n_text=Node # surely there is a better way to do this...
    classheader=\
"\nclass $nodetype$class_name$n_text(Node, $parentclass):
    \"\"\"$docstring\"\"\"
    bl_idname = \"$nodetype$class_name\"
    bl_label = \"$bl_label\"
    bl_icon = \"$icon\"
    
    def init(self, context):\n"
    printf "$(echo "$classheader")">classheader.txt
    
    #now do the cnode:
    echo "class $nodetype$class_name:" > cnode_def # this is the bl_idname!! important!
    echo "    '''A node representing an armature object'''" >> cnode_def
    echo >> cnode_def
    if [[ $nodetype == 'xForm' ]]; then
        echo "    bObject = None echo " >> cnode_def
        echo >> cnode_def
    fi
    
    echo "    def __init__(self, signature, base_tree):" >> cnode_def
    echo "        self.base_tree=base_tree" >> cnode_def
    echo "        self.executed = False" >> cnode_def
    echo "        self.signature = signature" >> cnode_def
    echo "        self.inputs = {" >> cnode_def
    
    echo > parameters
    
    if [[ $nodetype == 'xForm' ]]; then
        #node
        echo "        self.inputs.new('StringSocket', \"Name\")" >> classheader.txt
        echo "        self.inputs.new('MatrixSocket', \"Matrix\")" >> classheader.txt
        echo "        self.inputs.new('RelationshipSocket', \"Relationship\")" >> classheader.txt
        #cnode
        echo "          \"Name\"           : NodeSocket(is_input = True, name = \"Name\", node = self)," >> cnode_def
        echo "          \"Rotation Order\" : NodeSocket(is_input = True, name = \"Rotation Order\", node = self)," >> cnode_def
        echo "          \"Matrix\"         : NodeSocket(is_input = True, name = \"Matrix\", node = self)," >> cnode_def
        echo "          \"Relationship\"   : NodeSocket(is_input = True, name = \"Relationship\", node = self)," >> cnode_def
        #parameters; should be identical to cnode inputs
        echo "          \"Name\":None, " >> parameters
        echo "          \"Rotation Order\":None, " >> parameters
        echo "          \"Matrix\":None, " >> parameters
        echo "          \"Relationship\":None, " >> parameters
    elif [[ $nodetype == 'Link' ]]; then
        #node
        echo "        self.inputs.new (\"RelationshipSocket\", \"Input Relationship\")" >> classheader.txt
        #cnode
        echo "        \"Input Relationship\" : NodeSocket(is_input = True, name = \"Input Relationship\", node = self,)," >> cnode_def
        #parameters; should be identical to cnode inputs
        echo "        \"Input Relationship\":None, " >> parameters
    fi
    
    
    # New Inputs
    until [[ $num_inputs == "0" ]]; do
        sockettype=$(whiptail --title "add_node.sh" --menu "Input Socket Type" 25 78 16\
          "RelationshipSocket" ""\
          "MatrixSocket" "" \
          "xFormSocket" ""\
          "GenericRotationSocket" ""\
          "RelationshipSocket" ""\
          "xFormParameterSocket" ""\
          "DriverSocket" ""\
          "DriverVariableSocket" ""\
          "TransformSpaceSocket" ""\
          "BooleanSocket" ""\
          "BooleanThreeTupleSocket" ""\
          "RotationOrderSocket" ""\
          "QuaternionSocket" ""\
          "QuaternionSocketAA" ""\
          "IntSocket" ""\
	      "GeometrySocket" ""\
          "StringSocket" ""\
          "BoneCollectionSocket" ""\
          "BoolUpdateParentNode" ""\
          "LabelSocket" ""\
          "IKChainLengthSocket" ""\
          "EnumInheritScale" ""\
          "EnumRotationMix" ""\
          "EnumRotationMixCopyTransforms" ""\
          "EnumMaintainVolumeStretchTo" ""\
          "EnumRotationStretchTo" ""\
          "EnumTrackAxis" ""\
          "EnumUpAxis" ""\
          "EnumLockAxis" ""\
          "EnumLimitMode" ""\
          "EnumDriverVariableType" ""\
          "EnumDriverVariableEvaluationSpace" ""\
          "EnumDriverRotationMode" ""\
          "FloatSocket" ""\
          "FloatFactorSocket" ""\
          "FloatAngleSocket" ""\
          "VectorSocket" ""\
          "VectorEulerSocket" ""\
          "VectorTranslationSocket" ""\
          "VectorScaleSocket" ""\
          3>&2 2>&1 1>&3)
        socketname=$(whiptail --title "add_node.sh"\
          --inputbox "Input Socket Name" 8 39 "" 3>&1 1>&2 2>&3)
        cancelled=$?; check_cancelled
        ((num_inputs = num_inputs-1))
        #node
        echo "        self.inputs.new(\"$sockettype\", \"$socketname\")" >> classheader.txt
        #cnode
        echo "          \"$socketname\"   : NodeSocket(is_input = True, name = \"$socketname\", node = self)," >> cnode_def
        #parameters; should be identical to cnode inputs
        echo "          \"$socketname\":None, " >> parameters
    done
    
    echo "        }" >> cnode_def
    echo "        self.outputs = {" >> cnode_def
    
    # add the defaults for xForm, Link:
    if [[ $nodetype == 'xForm' ]]; then
        #node
        echo "        self.outputs.new('xFormSocket', \"xForm Out\")" >> classheader.txt
        #cnode
        echo "          \"xForm Out\" : NodeSocket(name=\"xForm Out\", node = self), }" >> cnode_def
    elif [[ $nodetype == 'Link' ]]; then
        #node
        echo "        self.outputs.new(\"RelationshipSocket\", \"Output Relationship\")" >> classheader.txt
        #cnode
        echo "          \"Output Relationship\" : NodeSocket(name = \"Output Relationship\", node=self), }" >> cnode_def
    # New Outputs
    elif [[ $nodetype == 'Utility' || $nodetype == 'Math' ]]; then
        
        until [[ $num_outputs == "0" ]]; do
            sockettype=$(whiptail --title "add_node.sh" --menu "Output Socket Type" 25 78 16\
            "RelationshipSocket" ""\
            "MatrixSocket" "" \
            "xFormSocket" ""\
            "GenericRotationSocket" ""\
            "RelationshipSocket" ""\
            "xFormParameterSocket" ""\
            "DriverSocket" ""\
            "DriverVariableSocket" ""\
            "TransformSpaceSocket" ""\
            "BooleanSocket" ""\
            "BooleanThreeTupleSocket" ""\
            "RotationOrderSocket" ""\
            "QuaternionSocket" ""\
            "QuaternionSocketAA" ""\
            "IntSocket" ""\
	        "GeometrySocket" ""\
            "StringSocket" ""\
            "BoneCollectionSocket" ""\
            "BoolUpdateParentNode" ""\
            "LabelSocket" ""\
            "IKChainLengthSocket" ""\
            "EnumInheritScale" ""\
            "EnumRotationMix" ""\
            "EnumRotationMixCopyTransforms" ""\
            "EnumMaintainVolumeStretchTo" ""\
            "EnumRotationStretchTo" ""\
            "EnumTrackAxis" ""\
            "EnumUpAxis" ""\
            "EnumLockAxis" ""\
            "EnumLimitMode" ""\
            "EnumDriverVariableType" ""\
            "EnumDriverVariableEvaluationSpace" ""\
            "EnumDriverRotationMode" ""\
            "FloatSocket" ""\
            "FloatFactorSocket" ""\
            "FloatAngleSocket" ""\
            "VectorSocket" ""\
            "VectorEulerSocket" ""\
            "VectorTranslationSocket" ""\
            "VectorScaleSocket" ""\
            3>&2 2>&1 1>&3)
            socketname=$(whiptail --title "add_node.sh"\
            --inputbox "Output Socket Name" 8 39 "" 3>&1 1>&2 2>&3)
            cancelled=$?; check_cancelled
            ((num_outputs = num_outputs-1))
            #node
            echo "        self.outputs.new(\"$sockettype\", \"$socketname\")" >> classheader.txt
            #cnode
            echo "          \"$socketname\" : NodeSocket(name = \"$socketname\", node=self)," >> cnode_def
            #parameters , this time it should by the cnode outputs!
            echo "          \"$socketname\":None, " >> parameters
        done
        echo "        }" >> cnode_def
    fi
    
    #cnode
    echo "        self.parameters = {" >> cnode_def
    cat parameters >> cnode_def
    echo "        }" >> cnode_def
    if [[ $nodetype == 'xForm' ]]; then
        echo "        self.links = {} # leave this empty for now!" >> cnode_def
        echo "        # now set up the traverse target..." >> cnode_def
        echo "        self.inputs["Relationship"].set_traverse_target(self.outputs["xForm Out"])" >> cnode_def
        echo "        self.outputs["xForm Out"].set_traverse_target(self.inputs["Relationship"])" >> cnode_def
        echo "        self.node_type = \"XFORM\"" >> cnode_def
    elif [[ $nodetype == 'Link' ]]; then
        echo "        # now set up the traverse target..." >> cnode_def
        echo "        self.inputs[\"Input Relationship\"].set_traverse_target(self.outputs[\"Output Relationship\"])" >> cnode_def
        echo "        self.outputs[\"Output Relationship\"].set_traverse_target(self.inputs[\"Input Relationship\"])" >> cnode_def
        echo "        self.node_type = \"LINK\"" >> cnode_def
    else
        echo "        self.node_type = \"UTILITY\"" >> cnode_def
    fi
    echo >> cnode_def
    echo "    def evaluate_input(self, input_name):" >> cnode_def
    echo "        return evaluate_input(self, input_name)" >> cnode_def
    echo >> cnode_def
    echo "    def bExecute(self, bContext = None,):" >> cnode_def
    echo "        return" >> cnode_def
    echo >> cnode_def
    echo "    def __repr__(self):" >> cnode_def
    echo "        return self.signature.__repr__()" >> cnode_def
    echo >> cnode_def    
    echo "    def fill_parameters(self):" >> cnode_def
    echo "        fill_parameters(self)" >> cnode_def
    # now it's done!
    
    cat cnode_def >> $cnodefile
    
    #time to fill upo the node definition
    echo "    def traverse(self, socket):" >> classheader.txt
    echo "        return default_traverse(self,socket)" >> classheader.txt
    
    # NODE FILE
    # operate on a duplicate of the file, use sed to rename.
    bakfile=$(echo $nodefile | sed s/.py/.bak.py/g)
    cp $nodefile $bakfile

    #find the line that is at the end of TellClasses:
    declare -i tc_end=$(grep -n -m 1 "]" $bakfile |  cut -f1 -d:)
    ((tc_end=$tc_end-1))
    # the total length of the file, in lines
    nodefile_len=$(cat $bakfile | wc -l)
    
    #get indentation level
    declare -i ind_level=$(head -n $tc_end $bakfile | tail -n 1 | grep -o " " | wc -l)
    
    #create the string (the class name with the proper indentation, ending in a comma).
    tc_line_add="$tc_line_add$nodetype$class_name$n_text"
    until [ $ind_level == 0 ]
    do
        tc_line_add=" $tc_line_add"
        ((ind_level--))
    done
    tc_line_add="$tc_line_add,"
    
    #slice the text, then add some stuff to the middle, then add the end back to it
    head -n $tc_end $bakfile > tmp
    echo "$tc_line_add" >> tmp
    ((tc_end=$tc_end+1))
    tail -n +$tc_end $bakfile >> tmp
    cp tmp $bakfile
    cat classheader.txt >> $bakfile # add the class
    
    cp $bakfile $nodefile
    rm $bakfile
    
    # __init__.py
    # operate on a duplicate of the file, use sed to rename.
    bakfile="__init__.bak.py"
    cp __init__.py $bakfile

    #find the line that marks the node category.
    declare -i tc_end
    if [[ $nodetype == 'Link' ]]; then
        tc_end=$(grep -n -m 1 "AllNodeCategory('LINK'"  $bakfile |  cut -f1 -d:)
    elif [[ $nodetype == 'xForm' ]]; then
        tc_end=$(grep -n -m 1 "AllNodeCategory('XFORM'" $bakfile |  cut -f1 -d:)
    elif [[ $nodetype == 'Utility' && $isinput == "0" ]]; then
        tc_end=$(grep -n -m 1 "AllNodeCategory('UTILITIES'" $bakfile |  cut -f1 -d:)
    elif [[ $nodetype == 'Utility' && $isinput == "1" ]]; then
        tc_end=$(grep -n -m 1 "AllNodeCategory('INPUT'" $bakfile |  cut -f1 -d:)
    elif [[ $nodetype == 'Math' ]]; then
        tc_end=$(grep -n -m 1 "AllNodeCategory('UTILITIES'" $bakfile |  cut -f1 -d:)
    fi
    
    # the total length of the file, in lines
    nodefile_len=$(cat $bakfile | wc -l)
    
    #get indentation level
    ((tc_end=$tc_end+1))
    declare -i ind_level=$(head -n $tc_end $bakfile | tail -n 1 | grep -o " " | wc -l)
    ((tc_end=$tc_end-1))
    
    #create the string (the class name with the proper indentation, ending in a comma).
    tc_line_add="NodeItem(\"$nodetype$class_name\")"
    until [ $ind_level == 0 ]
    do
        tc_line_add=" $tc_line_add"
        ((ind_level--))
    done
    tc_line_add="$tc_line_add,"
    
    #slice the text, then add some stuff to the middle, then add the end back to it
    head -n $tc_end $bakfile > tmp
    echo "$tc_line_add" >> tmp
    ((tc_end=$tc_end+1))
    tail -n +$tc_end $bakfile >> tmp
    cp tmp $bakfile
    cp $bakfile __init__.py
    rm $bakfile
    
    
    #clean up
    rm classheader.txt
    rm tmp
    rm cnode_def
    rm parameters
    
    # now we need to do the same for the container classes.
    whiptail --title "add_node.sh" --msgbox \
    "Finished adding node to addon!" 8 78
    
fi

