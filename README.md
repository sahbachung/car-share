# car-share

car-share is a Python library developed for _Programming the Internet of Things (PIoT)_.

## Requirements
- If the role of the host machine is set to Agent, the latest version of [OpenCV](opencv.org) and [dlib](http://dlib.net/) must be installed
You must also have a working webcam device connected to the host machine
- If the role is set to Master, the  and 
[Google Calendar API](https://developers.google.com/calendar/overview) must both be installed

## Installation


- `$ pip3 install -r car-share/requirements/[Agent, Master].txt`
- Alternatively, use `$ sh ./car-share/requirements/install.sh`
if the environment variable `$CAR_SHARE_ROLE` has been set

## Usage

To run the app, open the root directory as a python command:
```
$ cd ~/parent/dir/
$ python3 car-share [program] [-h] [-u USER] [-p] [-R Default] Master] Agent] [-C CONFIG]
```
Parameters
<table>
    <tr>
        <td><code>program</code></td>
        <td>
            program for the app to run
            <ul>
                <li><code>user</code> - user mode</li>
                <li><code>admin</code> - administration mode</li>
            </ul>
        </td>
        <td>required</td>
    </tr>
    <tr>
        <td><code>-u USER</code></td>
        <td>username for login</td>
        <td>optional</td>
    </tr>
    <tr>
        <td><code>-p</code></td>
        <td>prompt user for password</td>
        <td>optional<br/>default=False</td>
    </tr>
    <tr>
        <td><code>-R {Default, Master, Agent}</code></td>
        <td>
            override the environment var <code>CAR_SHARE_ROLE</code>
            <ul>
                <li><code>Default</code> - use environment variable to decide role</li>
                <li><code>Master</code> - start app as Master</li>
                <li><code>Agent</code> - start app as Agent</li>
            </ul>
        </td>
        <td>optional<br/>default="Default"</td>
    </tr>
    <tr>
        <td><code>-C CONFIG</code></td>
        <td>path to application configuration file</td>
        <td>optional<br>default="config.json"</td>
    </tr>
</table>

## Examples

```
$ python3 car-share user
$ python3 car-share admin -R Master
$ python3 car-share user -u root -p -R Master
$ python3 car-share user -R Agent -C path/my_config.json
```