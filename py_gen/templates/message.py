:: # Copyright 2013, Big Switch Networks, Inc.
:: #
:: # LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
:: # the following special exception:
:: #
:: # LOXI Exception
:: #
:: # As a special exception to the terms of the EPL, you may distribute libraries
:: # generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
:: # that copyright and licensing notices generated by LoxiGen are not altered or removed
:: # from the LoxiGen Libraries and the notice provided below is (i) included in
:: # the LoxiGen Libraries, if distributed in source code form and (ii) included in any
:: # documentation for the LoxiGen Libraries, if distributed in binary form.
:: #
:: # Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
:: #
:: # You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
:: # a copy of the EPL at:
:: #
:: # http::: #www.eclipse.org/legal/epl-v10.html
:: #
:: # Unless required by applicable law or agreed to in writing, software
:: # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
:: # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
:: # EPL for the specific language governing permissions and limitations
:: # under the EPL.
::
:: import itertools
:: from loxi_globals import OFVersions
:: import loxi_globals
:: import py_gen.util as util
:: import py_gen.oftype
:: include('_copyright.py')

:: include('_autogen.py')

import struct
import loxi
import const
import common
import action # for unpack_list
:: if version >= OFVersions.VERSION_1_1:
import instruction # for unpack_list
:: #endif
:: if version >= OFVersions.VERSION_1_3:
import meter_band # for unpack_list
:: #endif
import util
import loxi.generic_util

class Message(object):
    version = const.OFP_VERSION
    type = None # override in subclass
    xid = None

:: for ofclass in ofclasses:
:: include('_ofclass.py', ofclass=ofclass, superclass="Message")

:: #endfor

def parse_header(buf):
    if len(buf) < 8:
        raise loxi.ProtocolError("too short to be an OpenFlow message")
    return struct.unpack_from("!BBHL", buf)

def parse_message(buf):
    msg_ver, msg_type, msg_len, msg_xid = parse_header(buf)
    if msg_ver != const.OFP_VERSION and msg_type != const.OFPT_HELLO:
        raise loxi.ProtocolError("wrong OpenFlow version (expected %d, got %d)" % (const.OFP_VERSION, msg_ver))
    if len(buf) != msg_len:
        raise loxi.ProtocolError("incorrect message size")
    if msg_type in parsers:
        return parsers[msg_type](buf)
    else:
        raise loxi.ProtocolError("unexpected message type")

def parse_error(buf):
    if len(buf) < 8 + 2:
        raise loxi.ProtocolError("message too short")
    err_type, = struct.unpack_from("!H", buf, 8)
    if err_type in error_msg_parsers:
        return error_msg_parsers[err_type](buf)
    else:
        raise loxi.ProtocolError("unexpected error type %u" % err_type)

def parse_flow_mod(buf):
:: if version == OFVersions.VERSION_1_0:
:: offset = 57
:: elif version >= OFVersions.VERSION_1_1:
:: offset = 25
:: #endif
    if len(buf) < ${offset} + 1:
        raise loxi.ProtocolError("message too short")
    # Technically uint16_t for OF 1.0
    cmd, = struct.unpack_from("!B", buf, ${offset})
    if cmd in flow_mod_parsers:
        return flow_mod_parsers[cmd](buf)
    else:
        raise loxi.ProtocolError("unexpected flow mod cmd %u" % cmd)

:: if version >= OFVersions.VERSION_1_0:
def parse_group_mod(buf):
:: offset = 8
    if len(buf) < ${offset} + 2:
        raise loxi.ProtocolError("message too short")
    cmd, = struct.unpack_from("!H", buf, ${offset})
    if cmd in flow_mod_parsers:
        return group_mod_parsers[cmd](buf)
    else:
        raise loxi.ProtocolError("unexpected group mod cmd %u" % cmd)
:: #endif

def parse_stats_reply(buf):
    if len(buf) < 8 + 2:
        raise loxi.ProtocolError("message too short")
    stats_type, = struct.unpack_from("!H", buf, 8)
    if stats_type in stats_reply_parsers:
        return stats_reply_parsers[stats_type](buf)
    else:
        raise loxi.ProtocolError("unexpected stats type %u" % stats_type)

def parse_stats_request(buf):
    if len(buf) < 8 + 2:
        raise loxi.ProtocolError("message too short")
    stats_type, = struct.unpack_from("!H", buf, 8)
    if stats_type in stats_request_parsers:
        return stats_request_parsers[stats_type](buf)
    else:
        raise loxi.ProtocolError("unexpected stats type %u" % stats_type)

def parse_experimenter_stats_request(buf):
    if len(buf) < 24:
        raise loxi.ProtocolError("experimenter stats request message too short")

    experimenter, exp_type = struct.unpack_from("!LL", buf, 16)

    if experimenter in experimenter_stats_request_parsers and \
            exp_type in experimenter_stats_request_parsers[experimenter]:
        return experimenter_stats_request_parsers[experimenter][exp_type](buf)
    else:
        raise loxi.ProtocolError("unexpected stats request experimenter %#x exp_type %#x" % (experimenter, exp_type))

def parse_experimenter_stats_reply(buf):
    if len(buf) < 24:
        raise loxi.ProtocolError("experimenter stats reply message too short")

    experimenter, exp_type = struct.unpack_from("!LL", buf, 16)

    if experimenter in experimenter_stats_reply_parsers and \
            exp_type in experimenter_stats_reply_parsers[experimenter]:
        return experimenter_stats_reply_parsers[experimenter][exp_type](buf)
    else:
        raise loxi.ProtocolError("unexpected stats reply experimenter %#x exp_type %#x" % (experimenter, exp_type))

def parse_experimenter(buf):
    if len(buf) < 16:
        raise loxi.ProtocolError("experimenter message too short")

    experimenter, = struct.unpack_from("!L", buf, 8)
    if experimenter == 0x005c16c7: # Big Switch Networks
        subtype, = struct.unpack_from("!L", buf, 12)
    elif experimenter == 0x00002320: # Nicira
        subtype, = struct.unpack_from("!L", buf, 12)
    else:
        raise loxi.ProtocolError("unexpected experimenter id %#x" % experimenter)

    if subtype in experimenter_parsers[experimenter]:
        return experimenter_parsers[experimenter][subtype](buf)
    else:
        raise loxi.ProtocolError("unexpected experimenter %#x subtype %#x" % (experimenter, subtype))

parsers = {
:: sort_key = lambda x: x.type_members[1].value
:: msgtype_groups = itertools.groupby(sorted(ofclasses, key=sort_key), sort_key)
:: for (k, v) in msgtype_groups:
:: k = util.constant_for_value(version, "ofp_type", k)
:: v = list(v)
:: if len(v) == 1:
    ${k} : ${v[0].pyname}.unpack,
:: else:
    ${k} : parse_${k[11:].lower()},
:: #endif
:: #endfor
}

error_msg_parsers = {
    const.OFPET_HELLO_FAILED : hello_failed_error_msg.unpack,
    const.OFPET_BAD_REQUEST : bad_request_error_msg.unpack,
    const.OFPET_BAD_ACTION : bad_action_error_msg.unpack,
    const.OFPET_FLOW_MOD_FAILED : flow_mod_failed_error_msg.unpack,
    const.OFPET_PORT_MOD_FAILED : port_mod_failed_error_msg.unpack,
    const.OFPET_QUEUE_OP_FAILED : queue_op_failed_error_msg.unpack,
:: if version >= OFVersions.VERSION_1_1:
    const.OFPET_BAD_INSTRUCTION : bad_instruction_error_msg.unpack,
    const.OFPET_BAD_MATCH : bad_match_error_msg.unpack,
    const.OFPET_GROUP_MOD_FAILED : group_mod_failed_error_msg.unpack,
    const.OFPET_TABLE_MOD_FAILED : table_mod_failed_error_msg.unpack,
    const.OFPET_SWITCH_CONFIG_FAILED : switch_config_failed_error_msg.unpack,
:: #endif
:: if version >= OFVersions.VERSION_1_2:
    const.OFPET_ROLE_REQUEST_FAILED : role_request_failed_error_msg.unpack,
    const.OFPET_EXPERIMENTER : experimenter_error_msg.unpack,
:: #endif
:: if version >= OFVersions.VERSION_1_3:
    const.OFPET_METER_MOD_FAILED : meter_mod_failed_error_msg.unpack,
    const.OFPET_TABLE_FEATURES_FAILED : table_features_failed_error_msg.unpack,
:: #endif
}

flow_mod_parsers = {
    const.OFPFC_ADD : flow_add.unpack,
    const.OFPFC_MODIFY : flow_modify.unpack,
    const.OFPFC_MODIFY_STRICT : flow_modify_strict.unpack,
    const.OFPFC_DELETE : flow_delete.unpack,
    const.OFPFC_DELETE_STRICT : flow_delete_strict.unpack,
}

:: if version >= OFVersions.VERSION_1_1:
group_mod_parsers = {
    const.OFPGC_ADD : group_add.unpack,
    const.OFPGC_MODIFY : group_modify.unpack,
    const.OFPGC_DELETE : group_delete.unpack,
}
:: #endif

stats_reply_parsers = {
    const.OFPST_DESC : desc_stats_reply.unpack,
    const.OFPST_FLOW : flow_stats_reply.unpack,
    const.OFPST_AGGREGATE : aggregate_stats_reply.unpack,
    const.OFPST_TABLE : table_stats_reply.unpack,
    const.OFPST_PORT : port_stats_reply.unpack,
    const.OFPST_QUEUE : queue_stats_reply.unpack,
    const.OFPST_EXPERIMENTER : parse_experimenter_stats_reply,
:: if version >= OFVersions.VERSION_1_1:
    const.OFPST_GROUP : group_stats_reply.unpack,
    const.OFPST_GROUP_DESC : group_desc_stats_reply.unpack,
:: #endif
:: if version >= OFVersions.VERSION_1_2:
    const.OFPST_GROUP_FEATURES : group_features_stats_reply.unpack,
:: #endif
:: if version >= OFVersions.VERSION_1_3:
    const.OFPST_METER : meter_stats_reply.unpack,
    const.OFPST_METER_CONFIG : meter_config_stats_reply.unpack,
    const.OFPST_METER_FEATURES : meter_features_stats_reply.unpack,
    const.OFPST_TABLE_FEATURES : table_features_stats_reply.unpack,
    const.OFPST_PORT_DESC : port_desc_stats_reply.unpack,
:: #endif
}

stats_request_parsers = {
    const.OFPST_DESC : desc_stats_request.unpack,
    const.OFPST_FLOW : flow_stats_request.unpack,
    const.OFPST_AGGREGATE : aggregate_stats_request.unpack,
    const.OFPST_TABLE : table_stats_request.unpack,
    const.OFPST_PORT : port_stats_request.unpack,
    const.OFPST_QUEUE : queue_stats_request.unpack,
    const.OFPST_EXPERIMENTER : parse_experimenter_stats_request,
:: if version >= OFVersions.VERSION_1_1:
    const.OFPST_GROUP : group_stats_request.unpack,
    const.OFPST_GROUP_DESC : group_desc_stats_request.unpack,
:: #endif
:: if version >= OFVersions.VERSION_1_2:
    const.OFPST_GROUP_FEATURES : group_features_stats_request.unpack,
:: #endif
:: if version >= OFVersions.VERSION_1_3:
    const.OFPST_METER : meter_stats_request.unpack,
    const.OFPST_METER_CONFIG : meter_config_stats_request.unpack,
    const.OFPST_METER_FEATURES : meter_features_stats_request.unpack,
    const.OFPST_TABLE_FEATURES : table_features_stats_request.unpack,
    const.OFPST_PORT_DESC : port_desc_stats_request.unpack,
:: #endif
}

:: experimenter_ofclasses = [x for x in ofclasses if x.type_members[1].value == 4]
:: sort_key = lambda x: x.type_members[2].value
:: experimenter_ofclasses.sort(key=sort_key)
:: grouped = itertools.groupby(experimenter_ofclasses, sort_key)
experimenter_parsers = {
:: for (experimenter, v) in grouped:
    ${experimenter} : {
:: for ofclass in v:
        ${ofclass.type_members[3].value}: ${ofclass.pyname}.unpack,
:: #endfor
    },
:: #endfor
}

experimenter_stats_request_parsers = {
    0x005c16c7: {
:: if version >= OFVersions.VERSION_1_3:
        1: bsn_lacp_stats_request.unpack,
:: #endif
    },
}

experimenter_stats_reply_parsers = {
    0x005c16c7: {
:: if version >= OFVersions.VERSION_1_3:
        1: bsn_lacp_stats_reply.unpack,
:: #endif
    },
}
