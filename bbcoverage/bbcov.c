/*
 * Simple DynamoRIO instrumentation tool to record basic blocks hit
 * during application execution. 
 */

#include "dr_api.h"

file_t fpCoverageLog = INVALID_FILE;

static void event_exit(void);
static dr_emit_flags_t event_basic_block(void *drcontext, void *tag, instrlist_t *bb,
                                         bool for_trace, bool translating);
// DynamoRIO initialization function
DR_EXPORT void 
dr_init(client_id_t id)
{
    dr_register_exit_event(event_exit); //register exit callback
    dr_register_bb_event(event_basic_block); //register bb event callback
    // open log file for writting 
    fpCoverageLog = dr_open_file("bbcov.log",DR_FILE_WRITE_OVERWRITE | DR_FILE_ALLOW_LARGE);
	DR_ASSERT(fpCoverageLog != INVALID_FILE);    
    dr_fprintf(STDERR, "bbcov is running\n");
}

// Exit callback, just closes the log file
static void 
event_exit(void)
{
	dr_close_file(fpCoverageLog);
    dr_fprintf(STDERR,"bbcov finished\n");
}

// Basic block event callback. Called for each basic block hit. 
// Logs the basic block tag to the log file.
static dr_emit_flags_t
event_basic_block(void *drcontext, void *tag, instrlist_t *bb,
                  bool for_trace, bool translating)
{
    char bbTag[20];
    dr_snprintf(bbTag , sizeof(bbTag),PFX"\n",tag); 
	dr_write_file(fpCoverageLog,bbTag,sizeof(bbTag)-1);
    return DR_EMIT_DEFAULT;
}

