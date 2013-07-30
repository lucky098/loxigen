//:: # Copyright 2013, Big Switch Networks, Inc.
//:: #
//:: # LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
//:: # the following special exception:
//:: #
//:: # LOXI Exception
//:: #
//:: # As a special exception to the terms of the EPL, you may distribute libraries
//:: # generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
//:: # that copyright and licensing notices generated by LoxiGen are not altered or removed
//:: # from the LoxiGen Libraries and the notice provided below is (i) included in
//:: # the LoxiGen Libraries, if distributed in source code form and (ii) included in any
//:: # documentation for the LoxiGen Libraries, if distributed in binary form.
//:: #
//:: # Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
//:: #
//:: # You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
//:: # a copy of the EPL at:
//:: #
//:: # http::: #www.eclipse.org/legal/epl-v10.html
//:: #
//:: # Unless required by applicable law or agreed to in writing, software
//:: # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
//:: # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
//:: # EPL for the specific language governing permissions and limitations
//:: # under the EPL.
//::
//:: from loxi_ir import *
//:: import itertools
//:: import of_g
//:: include('_copyright.java')

//:: include('_autogen.java')

package ${msg.package};

//:: include("_imports.java", msg=msg)

class ${impl_class} implements ${msg.interface.name} {
    // version: ${version}
    private final static byte WIRE_VERSION = ${version.int_version};
//:: if msg.is_fixed_length:
    private final static int LENGTH = ${msg.length};
//:: else:
    private final static int MINIMUM_LENGTH = ${msg.min_length};
//:: #endif

//:: for prop in msg.data_members:
    private final static ${prop.java_type.public_type} ${prop.default_name} = ${prop.default_value};
//:: #end

    // OF message fields
//:: for prop in msg.data_members:
    private final ${prop.java_type.public_type} ${prop.name};
//:: #endfor

    ${impl_class}(${
        ", ".join("%s %s" %(prop.java_type.public_type, prop.name) for prop in msg.data_members) }) {
//:: for prop in msg.data_members:
        this.${prop.name} = ${prop.name};
//:: #endfor
    }

    // Accessors for OF message fields
//:: include("_field_accessors.java", msg=msg, generate_setters=False, builder=False)


    public ${msg.name}.Builder createBuilder() {
        return new BuilderImplWithParent(this);
    }

    static class BuilderImplWithParent implements ${msg.interface.name}.Builder {
        final ${impl_class} parentMessage;

        // OF message fields
//:: for prop in msg.data_members:
        private boolean ${prop.name}Set;
        private ${prop.java_type.public_type} ${prop.name};
//:: #endfor

        BuilderImplWithParent(${impl_class} parentMessage) {
            this.parentMessage = parentMessage;
        }

//:: include("_field_accessors.java", msg=msg, generate_setters=True, builder=True)

        @Override
        public ${msg.interface.name} getMessage() {
                return new ${impl_class}(
                    ${",\n                      ".join(
                         [ "this.{0}Set ? this.{0} : parentMessage.{0}".format(prop.name)
                             for prop in msg.data_members])}
                    );
        }
    }

    static class BuilderImpl implements ${msg.interface.name}.Builder {
        // OF message fields
//:: for prop in msg.data_members:
        private boolean ${prop.name}Set;
        private ${prop.java_type.public_type} ${prop.name};
//:: #endfor

//:: include("_field_accessors.java", msg=msg, generate_setters=True, builder=True)
//
        @Override
        public ${msg.interface.name} getMessage() {
            return new ${impl_class}(
                ${",\n                      ".join(
                     [ "this.{0}Set ? this.{0} : {1}.{2}".format(prop.name, impl_class, prop.default_name)
                         for prop in msg.data_members])}
                );
        }
    }

    final static Reader READER = new Reader();
    static class Reader implements OFMessageReader<${msg.interface.name}> {
        @Override
        public ${msg.interface.name} readFrom(ChannelBuffer bb) throws OFParseError {
//:: fields_with_length_member = {}
//:: for prop in msg.members:
//:: if prop.is_data:
            ${prop.java_type.public_type} ${prop.name} = ${prop.java_type.read_op(version,
                    length=fields_with_length_member[prop.c_name] if prop.c_name in fields_with_length_member else None)};
//:: elif prop.is_pad:
            // pad: ${prop.length} bytes
            bb.skipBytes(${prop.length});
//:: elif prop.is_fixed_value:
            // fixed value property ${prop.name} == ${prop.value}
            ${prop.java_type.priv_type} ${prop.name} = ${prop.java_type.read_op(version)};
            if(${prop.name} != ${prop.value})
                throw new OFParseError("Wrong ${prop.name}: Expected=${prop.enum_value}(${prop.value}), got="+${prop.name});
//:: elif prop.is_length_value:
            ${prop.java_type.public_type} ${prop.name} = ${prop.java_type.read_op(version)};
            if(${prop.name} < MINIMUM_LENGTH)
                throw new OFParseError("Wrong ${prop.name}: Expected to be >= " + MINIMUM_LENGTH + ", was: " + ${prop.name});
//:: elif prop.is_field_length_value:
//::        fields_with_length_member[prop.member.field_name] = prop.name
            int ${prop.name} = ${prop.java_type.read_op(version)};
//:: else:
    // fixme: todo ${prop.name}
//:: #endif
//:: #endfor
            return new ${impl_class}(
                    ${",\n                      ".join(
                         [ prop.name for prop in msg.data_members])}
                    );
        }
    }

    public int writeTo(ChannelBuffer bb) {
        return WRITER.write(bb, this);
    }

    final static Writer WRITER = new Writer();
    static class Writer implements OFMessageWriter<${impl_class}> {
        @Override
        public int write(ChannelBuffer bb, ${impl_class} message) {
//:: if not msg.is_fixed_length:
            int startIndex = bb.writerIndex();
//:: #end

//:: fields_with_length_member = {}
//:: for prop in msg.members:
//:: if prop.c_name in fields_with_length_member:
            int ${prop.name}StartIndex = bb.writerIndex();
//:: #endif
//:: if prop.is_data:
            ${prop.java_type.write_op(version, "message." + prop.name)};
//:: elif prop.is_pad:
            // pad: ${prop.length} bytes
            bb.writeZero(${prop.length});
//:: elif prop.is_fixed_value:
            // fixed value property ${prop.name} = ${prop.value}
            ${prop.java_type.write_op(version, prop.value)};
//:: elif prop.is_length_value:
            // ${prop.name} is length of variable message, will be updated at the end
            ${prop.java_type.write_op(version, 0)};
//:: elif prop.is_field_length_value:
//::        fields_with_length_member[prop.member.field_name] = prop.name
            // ${prop.name} is length indicator for ${prop.member.field_name}, will be
            // udpated when ${prop.member.field_name} has been written
            int ${prop.name}Index = bb.writerIndex();
            ${prop.java_type.write_op(version, 0)};
//:: else:
            // FIXME: todo write ${prop.name}
//:: #endif
//:: if prop.c_name in fields_with_length_member:
//::     length_member_name = fields_with_length_member[prop.c_name]
            // update field length member ${length_member_name}
            int ${prop.name}Length = bb.writerIndex() - ${prop.name}StartIndex;
            bb.setShort(${length_member_name}Index, ${prop.name}Length);
//:: #endif
//:: #endfor

//:: if msg.is_fixed_length:
            return LENGTH;
//:: else:
            // update length field
            int length = bb.writerIndex() - startIndex;
            bb.setShort(startIndex + 2, length);
            return length;
//:: #end

        }
    }


}