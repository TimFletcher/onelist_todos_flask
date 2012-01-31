# Add ability to check off completed items
ALTER TABLE onelist.`lists_listitem` ADD COLUMN `complete` tinyint(1) NOT NULL DEFAULT '0' AFTER `text`;